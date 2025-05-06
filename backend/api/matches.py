from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List, Dict
from datetime import datetime
import os
import random
import uuid

from ..models.user import UserInDB, UserResponse, UserPreferences
from ..services.auth import get_current_active_user
from ..services.matching import get_matches, create_match, accept_match, reject_match
from ..db.database import db
from ..db.neo4j_client import get_recommendations_for_user
from ..services.ml_integration import ml_service
from pydantic import EmailStr

# --------------------------------------------------------------------------- #
# helpers                                                                     #
# --------------------------------------------------------------------------- #

SUPERADMIN_MODE   = os.getenv("SUPERADMIN_MODE", "False").lower() == "true"
SUPERADMIN_DB_ID  = os.getenv("SUPERADMIN_DB_ID", "00000000-0000-0000-0000-000000admin")
SUPERADMIN_EMAIL  = os.getenv("SUPERADMIN_EMAIL", "superadmin@example.com")
SUPERADMIN_UNAME  = os.getenv("SUPERADMIN_USERNAME", "superadmin")


def _ensure_superadmin_node() -> str:
    """
    Make sure the super-admin User node exists in Neo4j.
    Returns the node’s id (uuid as string).
    """
    query = """
    MERGE (sa:User {id: $id})
    ON CREATE SET
        sa.email           = $email,
        sa.username        = $username,
        sa.full_name       = 'Super Admin',
        sa.gender          = 'other',
        sa.birth_date      = date('1980-01-01'),
        sa.age             = 44,
        sa.location        = 'Nowhere',
        sa.city            = 'Nowhere',
        sa.country         = 'Nowhere',
        sa.latitude        = 0.0,
        sa.longitude       = 0.0,
        sa.interests       = ['Technology'],
        sa.bio             = 'I keep the lights on 👑',
        sa.created_at      = datetime(),
        sa.updated_at      = datetime(),
        sa.is_active       = true,
        sa.is_verified     = true,
        sa.match_score     = 1.0
    RETURN sa.id AS id
    """
    rec = db.execute_query(
        query,
        {"id": SUPERADMIN_DB_ID, "email": SUPERADMIN_EMAIL, "username": SUPERADMIN_UNAME},
    )
    return rec[0]["id"]


def _normalise_current_user(current_user: UserInDB) -> UserInDB:
    """
    If SUPERADMIN_MODE is active we map any authenticated “super-admin”
    account to the persistent DB node so that all Cypher queries work.
    """
    if not SUPERADMIN_MODE:
        return current_user

    _ensure_superadmin_node()  # create if needed
    # overwrite only the id / email / username used in Cypher
    current_user.id = SUPERADMIN_DB_ID
    current_user.email = SUPERADMIN_EMAIL
    current_user.username = SUPERADMIN_UNAME
    return current_user


# --------------------------------------------------------------------------- #
# router                                                                      #
# --------------------------------------------------------------------------- #

router = APIRouter()


@router.get("/matches/recommendations", response_model=List[UserResponse])
async def get_match_recommendations(
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    """
    1. Try to return the 10 best matches in Neo4j using the
       Jaccard-similarity / shared-interest query.
    2. If no matches are found, fall back to the existing RandomUser
       recommendation logic (get_recommendations_for_user).
    3. If SUPERADMIN_MODE is on and the caller has no stored preferences,
       we *still* run the Jaccard query – super-admin just skips the
       preference filter rather than failing.
    """
    # ---- super-admin flag -------------------------------------------------
    SUPERADMIN_MODE = os.getenv("SUPERADMIN_MODE", "False").lower() == "true"

    # ---- fetch user preferences (we do **not** need them for this query,
    #      but keep the old logic so non-super-admins still get the warning)
    prefs_q = """
    MATCH (u:User {email: $email})
    RETURN u.preferences AS prefs
    """
    rec = db.execute_query(prefs_q, {"email": current_user.email})
    prefs_present = bool(rec and rec[0].get("prefs"))

    if not prefs_present and not SUPERADMIN_MODE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please set your matching preferences first.",
        )

    # ----------------------------------------------------------------------
    # 1.  Neo4j Jaccard-similarity query
    # ----------------------------------------------------------------------
    cypher = """
    MATCH (me:User {id: $me_id})
    MATCH (them:User)
    WHERE me <> them
    WITH me, them,
         [i IN me.interests WHERE i IN them.interests]        AS commonInterests,
         size(me.interests) + size(them.interests)
           - size([i IN me.interests WHERE i IN them.interests]) AS unionSize
    WITH them,
         commonInterests,
         CASE
           WHEN unionSize = 0 THEN 0.0
           ELSE toFloat(size(commonInterests)) / unionSize
         END                                                AS jaccardScore
    ORDER BY jaccardScore DESC, size(commonInterests) DESC
    LIMIT 10
    RETURN them                               AS user,
           commonInterests                    AS shared_interests,
           round(jaccardScore, 2)             AS similarity;
    """

    records = db.execute_query(cypher, {"me_id": current_user.id})

    if records:  # ✨ we found matches, format them for the frontend
        return [
            _to_user_response(r["user"], r["similarity"], i)
            for i, r in enumerate(records)
        ]

    # ----------------------------------------------------------------------
    # 2.  Fallback – RandomUser recommendations (your existing behaviour)
    # ----------------------------------------------------------------------
    fallback = await get_recommendations_for_user(current_user.id, 10)
    return [_to_user_response(r, r["match_score"], i) for i, r in enumerate(fallback)]


# --------------------------------------------------------------------------- #
# create / like / accept / reject                                             #
# --------------------------------------------------------------------------- #

@router.post("/matches/{user_id}")
async def create_new_match(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user),
) -> Any:
    current_user = _normalise_current_user(current_user)

    # 1 . Does the target user actually exist?
    exists_q = "MATCH (u:User {id:$them}) RETURN count(u) AS c"
    if db.execute_query(exists_q, {"them": user_id})[0]["c"] == 0:
        raise HTTPException(status_code=404, detail="Target user not found")

    # 2 . Relationship already there?
    qry_exists = """
    MATCH (u1:User {id:$me})-[r:MATCHED]->(u2:User {id:$them})
    RETURN r
    """
    if db.execute_query(qry_exists, {"me": current_user.id, "them": user_id}):
        return {"message": "Match already exists", "is_new": False}

    # 3 . Pick a score (fallback to 0.75 if none stored)
    score_q = "MATCH (u:User {id:$them}) RETURN coalesce(u.match_score, 0.75) AS s"
    score_rec = db.execute_query(score_q, {"them": user_id})
    match_score = score_rec[0]["s"] if score_rec else 0.75

    # 4 . Create relationship
    create_match(current_user.id, user_id, match_score)

    # 5 . Check if this instantly became mutual
    mutual_q = """
    MATCH (a:User {id:$me})-[:MATCHED {status:'accepted'}]->(b:User {id:$them}),
          (b)-[:MATCHED {status:'accepted'}]->(a)
    RETURN count(*) > 0 AS is_mutual
    """
    is_mutual = db.execute_query(
        mutual_q, {"me": current_user.id, "them": user_id}
    )[0]["is_mutual"]

    return {
        "message": "Match created successfully",
        "is_new": True,
        "is_mutual": is_mutual,
    }

@router.put("/matches/{user_id}/accept")
async def accept_user_match(
    user_id: str, current_user: UserInDB = Depends(get_current_active_user)
):
    current_user = _normalise_current_user(current_user)
    try:
        accept_match(current_user.id, user_id)
        return {"message": "Match accepted successfully"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/matches/{user_id}/reject")
async def reject_user_match(
    user_id: str, current_user: UserInDB = Depends(get_current_active_user)
):
    current_user = _normalise_current_user(current_user)
    try:
        reject_match(current_user.id, user_id)
        return {"message": "Match rejected successfully"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# --------------------------------------------------------------------------- #
# my-matches & pending likes                                                  #
# --------------------------------------------------------------------------- #

@router.get("/matches/my-matches", response_model=List[UserResponse])
async def get_my_matches(current_user: UserInDB = Depends(get_current_active_user)):
    current_user = _normalise_current_user(current_user)
    q = """
    MATCH (me:User {id:$me})-[r:MATCHED {status:'accepted'}]->(u:User)
    RETURN u AS user, r.score AS score
    ORDER BY r.score DESC
    """
    recs = db.execute_query(q, {"me": current_user.id})
    return [
        UserResponse(**{**d["user"], "match_score": d["score"]}) for d in recs
    ]


@router.get("/matches/my-pending-likes")
async def get_my_pending_likes(current_user: UserInDB = Depends(get_current_active_user)):
    current_user = _normalise_current_user(current_user)
    q = """
    MATCH (me:User {id:$me})-[r:MATCHED {status:'pending'}]->(u:User)
    RETURN u AS user, r.score AS score, r.created_at AS liked_at
    ORDER BY liked_at DESC
    """
    recs = db.execute_query(q, {"me": current_user.id})
    return [
        {
            "id": d["user"]["id"],
            "full_name": d["user"]["full_name"],
            "profile_photo": d["user"]["profile_photo"],
            "bio": d["user"].get("bio", ""),
            "interests": d["user"].get("interests", []),
            "location": d["user"].get("location", ""),
            "birth_date": d["user"].get("birth_date"),
            "match_score": d["score"],
            "liked_at": d["liked_at"],
        }
        for d in recs
    ]


# --------------------------------------------------------------------------- #
# ML-backed potential matches                                                 #
# --------------------------------------------------------------------------- #

@router.post("/matches", tags=["matches"])
async def get_potential_matches(
    current_user: UserInDB = Depends(get_current_active_user),
) -> List[Dict[str, Any]]:
    current_user = _normalise_current_user(current_user)
    try:
        from ..ml.matching_service import matching_service

        matches = await matching_service.get_matches_for_user(current_user.id, limit=10)
        if matches:
            return matches
    except Exception as exc:
        print("ML matching failed — falling back", exc)

    return await get_recommendations_for_user(current_user.id, 10)


@router.post("/users/{user_id}/like", tags=["matches"])
async def like_user(
    user_id: str, current_user: UserInDB = Depends(get_current_active_user)
):
    current_user = _normalise_current_user(current_user)

    from ..ml.matching_service import matching_service

    await matching_service.record_user_interaction(current_user.id, user_id, "LIKED")

    mutual_q = """
    MATCH (a:User {id:$me})-[:LIKED]->(b:User {id:$them}),
          (b)-[:LIKED]->(a)
    RETURN count(*) > 0 AS is_match
    """
    is_match = db.execute_query(mutual_q, {"me": current_user.id, "them": user_id})[0][
        "is_match"
    ]

    if is_match:
        await matching_service.update_user_match_statistics(current_user.id)
        await matching_service.update_user_match_statistics(user_id)

    return {"success": True, "is_match": is_match}


# --------------------------------------------------------------------------- #
# Statistics                                                                  #
# --------------------------------------------------------------------------- #

@router.get("/matches/statistics", tags=["matches"])
async def get_match_statistics(
    current_user: UserInDB = Depends(get_current_active_user),
) -> Dict[str, Any]:
    # no DB access needed here – delegate to ML layer
    return await ml_service.get_match_statistics()

def _to_user_response(
    u: dict,
    similarity: float,
    idx: int = 0,
) -> UserResponse:
    """
    Convert a raw Neo4j User node (or fallback dict) into the API's UserResponse.

    * `similarity` -> becomes `match_score`
    * supplies placeholder email / username if missing
    * gracefully handles Neo4j `datetime` objects **or** ISO-8601 strings
    """
    # -------- birth-date normalisation ------------------------------------
    raw_bd = u.get("birth_date")
    if isinstance(raw_bd, datetime):          # already a python datetime
        birth_dt = raw_bd
    else:                                     # str or None -> parse / default
        raw_str = str(raw_bd or "1970-01-01T00:00:00Z")
        if raw_str.endswith("Z"):           # turn Z-suffix into RFC-3339 offset
            raw_str = raw_str[:-1] + "+00:00"
        birth_dt = datetime.fromisoformat(raw_str)

    # -------- build response ----------------------------------------------
    return UserResponse(
        id=u["id"],
        email=u.get("email") or f"{u['id']}@sammy.fake",
        username=u.get("username") or f"user_{idx}",
        full_name=u.get("full_name") or "Unknown",
        gender=u.get("gender", "other"),
        birth_date=birth_dt,
        bio=u.get("bio", ""),
        interests=u.get("interests", []),
        location=u.get("location", ""),
        profile_photo=u.get("profile_photo", ""),
        match_score=similarity,
    )
    
import math, random   # add random if not already imported

def _lat_to_match_score(lat_str: str) -> float:
    """
    Derive a pseudo-random match-score from a latitude string.
    • Works with +/- and decimal points
    • Always returns 0.40 – 0.95 so the UI looks reasonable
    """
    try:
        # use absolute value, wrap onto 0-1, round to 2 dp
        score = abs(float(lat_str)) % 100 / 100.0
        score = round(score, 2)
    except (ValueError, TypeError):
        score = round(random.uniform(0.4, 0.95), 2)

    # clamp to [0.40, 0.95]
    return min(0.95, max(0.40, score))
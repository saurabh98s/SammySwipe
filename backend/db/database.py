from neo4j import GraphDatabase
from ..core.config import get_settings
from typing import Any

settings = get_settings()

class Neo4jDatabase:
    def __init__(self):
        self._driver = None

    def connect(self):
        if not self._driver:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
        return self._driver

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None

    def execute_query(self, query: str, parameters: dict = None) -> list[dict[str, Any]]:
        with self.connect().session() as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]

    def create_constraints(self):
        """Create necessary constraints for the database"""
        constraints = [
            "CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
            "CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE"
        ]
        
        with self.connect().session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    print(f"Error creating constraint: {e}")

# Global database instance
db = Neo4jDatabase() 
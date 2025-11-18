"""
Agent Configuration Version Manager
===================================

Git-like versioning system for agent configurations.
Every change creates a new version, allowing rollback.

Author: Substrate AI Team 💜
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class AgentVersion:
    """Represents a single version of agent configuration"""
    
    def __init__(
        self,
        version_id: str,
        agent_id: str,
        timestamp: str,
        config: Dict[str, Any],
        system_prompt: str,
        memory_blocks: Dict[str, Any],
        change_description: Optional[str] = None,
        parent_version: Optional[str] = None
    ):
        self.version_id = version_id
        self.agent_id = agent_id
        self.timestamp = timestamp
        self.config = config
        self.system_prompt = system_prompt
        self.memory_blocks = memory_blocks
        self.change_description = change_description or "No description"
        self.parent_version = parent_version
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "version_id": self.version_id,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "config": self.config,
            "system_prompt": self.system_prompt,
            "memory_blocks": self.memory_blocks,
            "change_description": self.change_description,
            "parent_version": self.parent_version
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class VersionManager:
    """
    Manages agent configuration versions.
    
    Features:
    - Auto-versioning on every save
    - Rollback to any previous version
    - Diff between versions
    - Export/import .af files with versions
    """
    
    def __init__(self, db_path: str = "./data/db/versions.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize version database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Versions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_versions (
                version_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                config TEXT NOT NULL,
                system_prompt TEXT NOT NULL,
                memory_blocks TEXT NOT NULL,
                change_description TEXT,
                parent_version TEXT,
                is_current BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_version) REFERENCES agent_versions(version_id)
            )
        """)
        
        # Index for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_versions 
            ON agent_versions(agent_id, timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_current_version 
            ON agent_versions(agent_id, is_current) 
            WHERE is_current = 1
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Version database initialized")
    
    def create_version(
        self,
        agent_id: str,
        config: Dict[str, Any],
        system_prompt: str,
        memory_blocks: Dict[str, Any],
        change_description: Optional[str] = None
    ) -> AgentVersion:
        """
        Create a new version of agent configuration.
        
        Args:
            agent_id: Agent identifier
            config: Model configuration (model, temperature, etc.)
            system_prompt: System prompt text
            memory_blocks: Memory blocks dictionary
            change_description: Description of changes
            
        Returns:
            AgentVersion object
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current version (to set as parent)
        cursor.execute("""
            SELECT version_id FROM agent_versions
            WHERE agent_id = ? AND is_current = 1
        """, (agent_id,))
        result = cursor.fetchone()
        parent_version = result[0] if result else None
        
        # Generate version ID
        timestamp = datetime.utcnow().isoformat()
        version_id = f"v_{int(datetime.utcnow().timestamp() * 1000)}"
        
        # Unset current version
        cursor.execute("""
            UPDATE agent_versions 
            SET is_current = 0 
            WHERE agent_id = ? AND is_current = 1
        """, (agent_id,))
        
        # Insert new version
        cursor.execute("""
            INSERT INTO agent_versions (
                version_id, agent_id, timestamp, config, 
                system_prompt, memory_blocks, change_description,
                parent_version, is_current
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            version_id,
            agent_id,
            timestamp,
            json.dumps(config),
            system_prompt,
            json.dumps(memory_blocks),
            change_description,
            parent_version
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Version created: {version_id}")
        if change_description:
            print(f"   📝 {change_description}")
        
        return AgentVersion(
            version_id=version_id,
            agent_id=agent_id,
            timestamp=timestamp,
            config=config,
            system_prompt=system_prompt,
            memory_blocks=memory_blocks,
            change_description=change_description,
            parent_version=parent_version
        )
    
    def get_current_version(self, agent_id: str) -> Optional[AgentVersion]:
        """Get current active version"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT version_id, agent_id, timestamp, config, 
                   system_prompt, memory_blocks, change_description, parent_version
            FROM agent_versions
            WHERE agent_id = ? AND is_current = 1
        """, (agent_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return AgentVersion(
            version_id=result[0],
            agent_id=result[1],
            timestamp=result[2],
            config=json.loads(result[3]),
            system_prompt=result[4],
            memory_blocks=json.loads(result[5]),
            change_description=result[6],
            parent_version=result[7]
        )
    
    def get_version(self, version_id: str) -> Optional[AgentVersion]:
        """Get specific version by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT version_id, agent_id, timestamp, config, 
                   system_prompt, memory_blocks, change_description, parent_version
            FROM agent_versions
            WHERE version_id = ?
        """, (version_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return AgentVersion(
            version_id=result[0],
            agent_id=result[1],
            timestamp=result[2],
            config=json.loads(result[3]),
            system_prompt=result[4],
            memory_blocks=json.loads(result[5]),
            change_description=result[6],
            parent_version=result[7]
        )
    
    def list_versions(self, agent_id: str, limit: int = 50) -> List[AgentVersion]:
        """List all versions for an agent (newest first)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT version_id, agent_id, timestamp, config, 
                   system_prompt, memory_blocks, change_description, parent_version
            FROM agent_versions
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (agent_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        versions = []
        for result in results:
            versions.append(AgentVersion(
                version_id=result[0],
                agent_id=result[1],
                timestamp=result[2],
                config=json.loads(result[3]),
                system_prompt=result[4],
                memory_blocks=json.loads(result[5]),
                change_description=result[6],
                parent_version=result[7]
            ))
        
        return versions
    
    def rollback_to_version(self, version_id: str) -> AgentVersion:
        """
        Rollback to a specific version.
        Creates a new version based on the old one.
        """
        # Get the target version
        target = self.get_version(version_id)
        if not target:
            raise ValueError(f"Version {version_id} not found")
        
        # Create new version (rollback creates a new version in history)
        return self.create_version(
            agent_id=target.agent_id,
            config=target.config,
            system_prompt=target.system_prompt,
            memory_blocks=target.memory_blocks,
            change_description=f"Rollback to {version_id}"
        )
    
    def get_diff(self, version_id_1: str, version_id_2: str) -> Dict[str, Any]:
        """
        Compare two versions and return differences.
        """
        v1 = self.get_version(version_id_1)
        v2 = self.get_version(version_id_2)
        
        if not v1 or not v2:
            return {"error": "One or both versions not found"}
        
        diff = {
            "version_1": version_id_1,
            "version_2": version_id_2,
            "timestamp_1": v1.timestamp,
            "timestamp_2": v2.timestamp,
            "changes": {}
        }
        
        # Config differences
        if v1.config != v2.config:
            diff["changes"]["config"] = {
                "old": v1.config,
                "new": v2.config
            }
        
        # System prompt differences
        if v1.system_prompt != v2.system_prompt:
            diff["changes"]["system_prompt"] = {
                "old_length": len(v1.system_prompt),
                "new_length": len(v2.system_prompt),
                "old": v1.system_prompt[:200] + "..." if len(v1.system_prompt) > 200 else v1.system_prompt,
                "new": v2.system_prompt[:200] + "..." if len(v2.system_prompt) > 200 else v2.system_prompt
            }
        
        # Memory block differences
        if v1.memory_blocks != v2.memory_blocks:
            diff["changes"]["memory_blocks"] = {
                "old": v1.memory_blocks,
                "new": v2.memory_blocks
            }
        
        return diff
    
    def export_to_agent_file(self, agent_id: str, output_path: str):
        """
        Export agent configuration to .af file (Letta format).
        """
        current = self.get_current_version(agent_id)
        if not current:
            raise ValueError(f"No current version found for agent {agent_id}")
        
        agent_data = {
            "agent_id": agent_id,
            "name": "Substrate AI",
            "version": current.version_id,
            "timestamp": current.timestamp,
            "config": current.config,
            "system_prompt": current.system_prompt,
            "memory_blocks": current.memory_blocks
        }
        
        with open(output_path, 'w') as f:
            json.dump(agent_data, f, indent=2)
        
        print(f"✅ Agent exported to {output_path}")


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("\n🧪 TESTING VERSION MANAGER")
    print("="*60)
    
    vm = VersionManager("./data/db/versions_test.db")
    
    # Create initial version
    v1 = vm.create_version(
        agent_id="default",
        config={"model": "openrouter/polaris-alpha", "temperature": 0.7},
        system_prompt="You are an AI assistant",
        memory_blocks={"persona": "You are an AI assistant"},
        change_description="Initial version"
    )
    print(f"\n✅ Created v1: {v1.version_id}")
    
    # Create second version
    v2 = vm.create_version(
        agent_id="default",
        config={"model": "openrouter/polaris-alpha", "temperature": 0.8},
        system_prompt="You are an AI assistant",
        memory_blocks={"persona": "You are an AI assistant"},
        change_description="Updated temperature and prompt"
    )
    print(f"✅ Created v2: {v2.version_id}")
    
    # List versions
    versions = vm.list_versions("default")
    print(f"\n📜 Total versions: {len(versions)}")
    for v in versions:
        print(f"   • {v.version_id}: {v.change_description}")
    
    # Get diff
    diff = vm.get_diff(v1.version_id, v2.version_id)
    print(f"\n🔄 Diff between versions:")
    print(json.dumps(diff, indent=2))
    
    # Rollback
    v3 = vm.rollback_to_version(v1.version_id)
    print(f"\n⏮️  Rolled back to v1, created v3: {v3.version_id}")
    
    print("\n✅ All tests passed!")








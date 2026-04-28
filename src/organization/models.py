"""
organization/models.py - Org chart, governance, and system prompt assembly.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

@dataclass
class OrganizationConfig:
    agent_name: str = ""
    agent_role: str = ""
    agent_responsibilities: str = ""
    agent_behavioral_guidelines: str = ""
    superiors: list = field(default_factory=list)
    peers: list = field(default_factory=list)
    subordinates: list = field(default_factory=list)
    governance_rules: list = field(default_factory=list)
    document_briefings: list = field(default_factory=list)
    created_at: str = ""
    last_modified: str = ""

    def add_member(self, name, role, relationship, description=""):
        m = {"name": name, "role": role, "description": description, "relationship": relationship}
        if relationship == "superior": self.superiors.append(m)
        elif relationship == "peer": self.peers.append(m)
        elif relationship == "subordinate": self.subordinates.append(m)
        self.last_modified = datetime.now().isoformat()

    def add_governance_rule(self, target_role, rules, priority="standard"):
        self.governance_rules.append({"target_role": target_role, "rules": rules, "priority": priority})
        self.last_modified = datetime.now().isoformat()

    def add_document_briefing(self, filename, rationale, chunk_count=0):
        self.document_briefings.append({
            "filename": filename, "rationale": rationale,
            "upload_time": datetime.now().isoformat(), "chunk_count": chunk_count,
        })
        self.last_modified = datetime.now().isoformat()

    def get_all_roles(self):
        roles = []
        for m in self.superiors:
            roles.append({"name": m["name"], "role": m["role"], "relationship": "superior"})
        for m in self.peers:
            roles.append({"name": m["name"], "role": m["role"], "relationship": "peer"})
        for m in self.subordinates:
            roles.append({"name": m["name"], "role": m["role"], "relationship": "subordinate"})
        return roles

    def build_system_prompt(self):
        sections = []
        sections.append(
            f"You are {self.agent_name}, serving as {self.agent_role} "
            f"in this organization.\n\nYour responsibilities:\n{self.agent_responsibilities}"
        )
        if self.superiors:
            lines = ["Your superiors (you report to them):"]
            for m in self.superiors:
                desc = f" -- {m['description']}" if m.get("description") else ""
                lines.append(f"  - {m['name']}, {m['role']}{desc}")
            sections.append("\n".join(lines))
        if self.peers:
            lines = ["Your peers (same organizational level):"]
            for m in self.peers:
                desc = f" -- {m['description']}" if m.get("description") else ""
                lines.append(f"  - {m['name']}, {m['role']}{desc}")
            sections.append("\n".join(lines))
        if self.subordinates:
            lines = ["Your subordinates (they report to you):"]
            for m in self.subordinates:
                desc = f" -- {m['description']}" if m.get("description") else ""
                lines.append(f"  - {m['name']}, {m['role']}{desc}")
            sections.append("\n".join(lines))
        if self.governance_rules:
            lines = ["Governance frameworks for your interactions:"]
            for g in self.governance_rules:
                pt = f" [PRIORITY: {g['priority'].upper()}]" if g.get("priority", "standard") != "standard" else ""
                lines.append(f"\n  When interacting with {g['target_role']}{pt}:\n  {g['rules']}")
            sections.append("\n".join(lines))
        if self.agent_behavioral_guidelines:
            sections.append(f"Behavioral guidelines:\n{self.agent_behavioral_guidelines}")
        if self.document_briefings:
            lines = ["You have been briefed on the following documents. Refer to them when relevant:"]
            for d in self.document_briefings:
                lines.append(f"  - {d['filename']}: {d['rationale']} ({d.get('chunk_count', 0)} sections indexed)")
            sections.append("\n".join(lines))
        return "\n\n".join(sections)

    def to_dict(self):
        return {k: getattr(self, k) for k in [
            "agent_name", "agent_role", "agent_responsibilities",
            "agent_behavioral_guidelines", "superiors", "peers", "subordinates",
            "governance_rules", "document_briefings", "created_at", "last_modified",
        ]}

    @classmethod
    def from_dict(cls, data):
        c = cls()
        for k, v in data.items():
            if hasattr(c, k): setattr(c, k, v)
        return c

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

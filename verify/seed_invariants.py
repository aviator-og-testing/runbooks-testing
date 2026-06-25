"""Seed this app's baseline invariants into the local mergeit database.

Run via `just verify-invariants`. Reads `verify/baseline-invariants.yaml`,
deletes the existing `[AUTOGEN]`-titled invariants for this repo's account, and
recreates them from the fixture. Idempotent: edit the YAML, re-run.

Config (env):
  MERGEIT_DATABASE_URL  Postgres DSN for the local mergeit DB.
                        Default: postgresql://mergeit:1q2w3e4r@localhost:5432/mergeit
  REPO_FULL_NAME        owner/repo to scope the invariants to.
                        Default: derived from `git remote get-url origin`.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys

import psycopg
import yaml

TITLE_PREFIX = "[AUTOGEN] "
DEFAULT_DSN = "postgresql://mergeit@localhost:5432/mergeit"

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "verify" / "baseline-invariants.yaml"


def repo_full_name() -> str:
    name = os.environ.get("REPO_FULL_NAME")
    if name:
        return name
    url = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "remote", "get-url", "origin"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    # https://github.com/owner/repo.git  or  git@github.com:owner/repo.git
    path = url.split("github.com", 1)[-1].lstrip(":/")
    return path.removesuffix(".git")


def main() -> int:
    dsn = os.environ.get("MERGEIT_DATABASE_URL", DEFAULT_DSN)
    repo = repo_full_name()
    invariants = yaml.safe_load(FIXTURE.read_text())

    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, account_id FROM github_repo WHERE lower(name) = lower(%s)",
            (repo,),
        )
        row = cur.fetchone()
        if not row:
            print(f"error: repo {repo!r} is not connected to the local account", file=sys.stderr)
            return 1
        repo_id, account_id = row

        cur.execute(
            "SELECT id FROM baseline_invariant WHERE account_id = %s AND title LIKE %s",
            (account_id, TITLE_PREFIX + "%"),
        )
        old_ids = [r[0] for r in cur.fetchall()]
        if old_ids:
            # Drop repo links first; invariant_condition rows cascade on delete.
            cur.execute(
                "DELETE FROM baseline_invariant_repo WHERE baseline_invariant_id = ANY(%s)",
                (old_ids,),
            )
            cur.execute("DELETE FROM baseline_invariant WHERE id = ANY(%s)", (old_ids,))

        for inv in invariants:
            cur.execute(
                "SELECT id FROM invariant_category WHERE account_id = %s AND slug = %s",
                (account_id, inv["category"]),
            )
            crow = cur.fetchone()
            if not crow:
                print(f"error: unknown invariant category {inv['category']!r}", file=sys.stderr)
                return 1
            cur.execute(
                "INSERT INTO baseline_invariant (account_id, category_id, title, body, created, modified) "
                "VALUES (%s, %s, %s, %s, now(), now()) RETURNING id",
                (account_id, crow[0], TITLE_PREFIX + inv["title"], inv["body"].strip()),
            )
            inv_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO baseline_invariant_repo (baseline_invariant_id, repo_id) VALUES (%s, %s)",
                (inv_id, repo_id),
            )
            for cond in inv.get("conditions") or []:
                cur.execute(
                    "INSERT INTO invariant_condition (invariant_id, type, value, negate, created, modified) "
                    "VALUES (%s, %s, %s, %s, now(), now())",
                    (inv_id, cond["type"], cond["value"], bool(cond.get("negate", False))),
                )
        conn.commit()

    print(f"seeded {len(invariants)} baseline invariants for {repo} (replaced {len(old_ids)} existing)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

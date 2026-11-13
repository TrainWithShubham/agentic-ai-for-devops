# Catalog API deployment process

Document ID: deploy-process. Version 3. Updated 2026-11-13. Synthetic training material.

Deploy a reviewed commit to staging first. Run the smoke test against /health and /catalog before promoting the same image digest to production. A successful image build alone does not establish application health.

Production promotion requires a release-manager approval. Record the image digest, change ticket and previous healthy digest before promotion. Never use a mutable latest tag as the rollback reference.

For a production rollback, restore the previous verified image digest. Run /health and /catalog smoke tests again and monitor the error rate. Use the rollback checklist for the approval and validation steps.

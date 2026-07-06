#!/usr/bin/env python3

from flask import Flask, request
import subprocess
import datetime

app = Flask(__name__)

# ===========================
# Configuration
# ===========================

TARGET_BRANCH = "main"

PLAYBOOK = "/home/ec2-user/ansible-project/ci-pipeline.yml"
INVENTORY = "/etc/ansible/hosts"

# ===========================
# Webhook Endpoint
# ===========================

@app.route("/github", methods=["POST"])
def github_webhook():

    payload = request.get_json()

    if payload is None:
        print("Received invalid payload")
        return "Invalid Payload", 400

    branch = payload.get("ref", "")

    print("\n===================================")
    print("Webhook received")
    print("Time :", datetime.datetime.now())
    print("Branch :", branch)

    if branch == f"refs/heads/{TARGET_BRANCH}":

        print("Change detected on target branch.")
        print("Running Ansible Playbook...")

        result = subprocess.run(
            [
                "ansible-playbook",
                "-i",
                INVENTORY,
                PLAYBOOK
            ],
            capture_output=True,
            text=True
        )

        print("------------ PLAYBOOK OUTPUT ------------")
        print(result.stdout)

        if result.returncode != 0:
            print("Playbook Failed")
            print(result.stderr)
            return "Failed",500

        print("Playbook Executed Successfully")

        return "OK",200

    else:

        print("Push received for another branch.")
        print("Ignoring...")

        return "Ignored",200


# ===========================
# Main
# ===========================

if __name__ == "__main__":

    print("========================================")
    print(" GitHub Webhook Listener Started")
    print(" Listening on Port 5000")
    print(" Waiting for GitHub Push Events...")
    print("========================================")

    app.run(
        host="0.0.0.0",
        port=5000
    )

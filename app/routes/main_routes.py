"""
Main View Routes for Modern Cyber SOC Dashboard
Ransomware Attack & Defense Interactive Simulator
"""

from flask import Blueprint, render_template, current_app

main_bp = Blueprint("main", __name__)


def _get_crypto_engine():
    return current_app.extensions["crypto_engine"]


def _get_defense_engine():
    return current_app.extensions["defense_engine"]


@main_bp.route("/")
def index():
    """Main SOC Dashboard: Live file explorer, status gauges, quick action panel."""
    crypto = _get_crypto_engine()
    fingerprint = crypto.get_key_fingerprint()
    return render_template("index.html", key_fingerprint=fingerprint, active_page="dashboard")


@main_bp.route("/lab/attack")
def attack_lab():
    """Attack Lifecycle Lab: Step-by-step hybrid encryption visualizer & C2 inspector."""
    crypto = _get_crypto_engine()
    return render_template(
        "attack_lab.html",
        c2_public_key=crypto.get_public_key_pem(),
        c2_private_key=crypto.get_private_key_pem(),
        key_fingerprint=crypto.get_key_fingerprint(),
        active_page="attack_lab",
    )


@main_bp.route("/lab/defense")
def defense_lab():
    """Defense Lab: Shannon entropy analyzer, Canary tripwires, Snapshot rollback."""
    return render_template("defense_lab.html", active_page="defense_lab")


@main_bp.route("/lab/calculator")
def calculator():
    """Brute-Force Feasibility Calculator: Demonstrates why modern encryption cannot be broken."""
    return render_template("calculator.html", active_page="calculator")


@main_bp.route("/theory")
def theory():
    """Theory Guide: Cryptovirology, Hybrid Encryption, MITRE ATT&CK T1486, Incident Response."""
    return render_template("theory.html", active_page="theory")

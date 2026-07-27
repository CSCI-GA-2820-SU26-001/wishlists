"""
Environment setup for Behave BDD tests
"""

import os


def before_all(context):
    """Executed before all BDD scenarios"""
    context.base_url = os.getenv("BASE_URL", "http://localhost:8080/")
    context.driver = None


def after_scenario(context, scenario):
    """Executed after each BDD scenario"""
    if context.driver:
        context.driver.quit()
        context.driver = None

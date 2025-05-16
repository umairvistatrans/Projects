# -*- coding: utf-8 -*-

import logging

from . import models
from . import controllers

_logger = logging.getLogger(__name__)

def _malex_post_initialisation(env):
    """
        Post-initialization method to search for the model 'submission.request'
        and set its 'website_form_access' to True if it exists.
        """
    try:
        # Check if the model 'submission.request' exists in the system
        model_obj = env['ir.model'].search([('model', '=', 'submission.request')], limit=1)
        if model_obj:
            # Update 'website_form_access' to True
            model_obj.write({'website_form_access': True})
            _logger.info("'website_form_access' set to True for 'submission.request'.")
        else:
            _logger.warning("Model 'submission.request' not found in the system.")

    except Exception as e:
        _logger.error(f"Error in _malex_post_initialisation: {e}")

    try:
        submissions_menu = env.ref('portal_management_mlx.menu_submissions_mlx')
        top_menu = env['website.menu'].search([('url', '=', '/default-main-menu'), ('name', '=', 'Top Menu for Website 1')], limit=1)
        submissions_menu.write({'parent_id': top_menu.id})
        _logger.info("Submissions menu set up in the navbar for default website.")

    except Exception as e:
        _logger.error(f"Error in _malex_post_initialisation: {e}")

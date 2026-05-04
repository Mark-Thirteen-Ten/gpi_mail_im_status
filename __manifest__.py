# -*- coding: utf-8 -*-
{
    "name": "GPI Mail IM Status",
    "summary": "Odoo 19 style IM status controls for Odoo 17",
    "description": "Adds online/away/do-not-disturb/offline IM status controls and DND notification suppression.",
    "author": "GPI",
    "website": "https://github.com/mark-thirteen-ten",
    "category": "Discuss",
    "version": "17.0.1.0.0",
    "depends": ["bus", "mail", "web"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "gpi_mail_im_status/static/src/**/*.js",
            "gpi_mail_im_status/static/src/**/*.xml"
        ]
    },
    "installable": True,
    "application": False,
}

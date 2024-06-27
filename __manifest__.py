{
    "name": "Radio",
    "version": "17.0",
    "category": "",
    "summary": "Summary",
    "description": """ Description """,
    "depends": [
        "web",
        "auto_create_user",
        "website",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/station_views.xml",
        "views/res_country_views.xml",
        "views/res_lang_views.xml",
        "views/page_views.xml",
    ],

    'assets': {
        'web.assets_backend': [
            'radio/static/src/js/player.js',
            'radio/static/src/xml/player.xml',
            'radio/static/src/css/radio.scss',
            'radio/static/src/css/radio.css',
        ],
    },
    "application": True,
}

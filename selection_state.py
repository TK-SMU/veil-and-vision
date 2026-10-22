"""Explicit user choices, independent of decorative artwork and defaults."""
def selected(app, group, value):
    if group=='selected_background':return app.settings.get('selected_background')==value
    return app.settings.get('selection_choices', {}).get(group) == value


def choose(app, group, value):
    if group=="selected_background":
        app.store.settings(selected_background=value)
        return
    choices=dict(app.settings.get('selection_choices', {}))
    choices[group]=value
    app.store.settings(selection_choices=choices)


def fresh(app):
    # Keep global preferences, but never carry a visitor's reading choices over.
    choices=dict(app.settings.get('selection_choices', {}))
    for key in ('hat','buddy','accessory','selected_background','oracle-tabs','intentions','meaning-tabs'):
        choices.pop(key,None)
    app.store.settings(selection_choices=choices,hat='Star',buddy='Cat',accessory='Bow',selected_background=None)
    app.category='Hats'
    app.meaning_tab='Meaning'

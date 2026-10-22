"""Quiet shared effects, independent of background music."""
import json

def play(app,name):
    if not name or not getattr(app,'settings',{}).get('sound',False):return
    try:
        if app.sound:app.sound.effect(name)
    except Exception:
        # Missing sound files or audio devices must never interrupt the UI.
        pass

def snapshot(app):
    return dict(screen=app.screen,settings=json.dumps(app.settings,sort_keys=True),
                music=app.settings.get('music'),sound=app.settings.get('sound'),
                category=getattr(app,'category',None),tab=getattr(app,'meaning_tab',None),
                step=(app.reading or {}).get('step'),drafts=repr(getattr(app,'followup_drafts',{})),
                diary=repr(app.store.data.get('readings',[])))

def after_action(app,before):
    if getattr(app,'_quiet_action',False):return
    after=snapshot(app);old=before['screen'];new=after['screen']
    if before['music']!=after['music'] or before['sound']!=after['sound']:name='toggle'
    elif new=='save' and old!='save':name='save_chime'
    elif old=='followup' and new=='diary' and before['diary']!=after['diary']:name='save_chime'
    elif old!=new:
        if new=='diary' or old=='diary':name='page_turn'
        elif new in ('oracle','intention','draw','reading','reflect'):name='select_crystal'
        else:name='ui_click'
    elif before['category']!=after['category'] or before['tab']!=after['tab']:name='ui_click'
    elif before['settings']!=after['settings'] or before['step']!=after['step'] or before['drafts']!=after['drafts']:name='select_crystal'
    else:return  # Typing, hovering and opening an input are silent.
    play(app,name)

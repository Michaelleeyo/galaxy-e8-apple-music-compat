"""E8 UI-only patches for the audited 35 baseline. External smali inputs only."""
import argparse,re
from pathlib import Path
SONG='Ldev/amenhancer/module/hook/tabletmedia/TabletSongColumnLayout;'
GEOM='Ldev/amenhancer/module/hook/TabletArtworkLayoutPolicy$SongColumn;'
VOLUME='Ldev/amenhancer/module/hook/tabletmedia/IosVolumeSliderView;'

def once(text,old,new):
    if text.count(old)!=1:raise ValueError('Expected unique audited patch anchor')
    return text.replace(old,new,1)

def patch_knockout(text):
    if '# E8 bitmap canvas density' in text:raise ValueError('Density patch already applied')
    start=text.index('.method public final draw(Landroid/graphics/Canvas;)V')
    end=text.index('.end method',start);body=text[start:end]
    if '.registers 10' not in body:raise ValueError('Unexpected draw register layout')
    anchor='    new-instance v3, Landroid/graphics/Canvas;'
    code=r'''
    # E8 bitmap canvas density: avoid rescaling pixel-sized backing buffers.
    invoke-virtual {p1}, Landroid/graphics/Canvas;->getDensity()I
    move-result v5
    invoke-virtual {v0, v5}, Landroid/graphics/Bitmap;->setDensity(I)V
    invoke-virtual {v1, v5}, Landroid/graphics/Bitmap;->setDensity(I)V

'''
    return text[:start]+once(body,anchor,code+anchor)+text[end:]

def patch_song_column(text):
    if 'carVerticalOffset(' in text:raise ValueError('Car layout patch already applied')
    anchor='.method private final place(Landroid/view/View;IIII)V\n    .registers 9\n'
    code=fr'''
    # E8 removes only these two supplemental controls, including hit targets.
    iget-object v0, p0, {SONG}->volume:{VOLUME}
    if-eq p1, v0, :e8_hidden_control
    iget-object v0, p0, {SONG}->output:Landroid/widget/ImageButton;
    if-ne p1, v0, :e8_keep_control
    :e8_hidden_control
    const/16 v0, 0x8
    invoke-virtual {{p1, v0}}, Landroid/view/View;->setVisibility(I)V
    return-void
    :e8_keep_control
'''
    text=once(text,anchor,anchor+code)
    # Keep original layout/animation code, but never start invisible volume polling.
    pattern=r'    invoke-virtual \{([^,}]+), [^}]+\}, '+re.escape(VOLUME)+r'->setPageVisible\(Z\)V'
    text,count=re.subn(pattern,lambda m:'    invoke-static {'+m[1]+'}, '+SONG+'->carHideVolume('+VOLUME+')V',text)
    if count!=4:raise ValueError('Unexpected volume lifecycle call count')
    start=text.index('.method public final geometry(II)');end=text.index('.end method',start)
    body=text[start:end]
    anchor='    .line 268\n    invoke-static/range {v5 .. v37}, '+GEOM+'->copy$default'
    code=fr'''
    # E8 centers the visible drag/cover/metadata/transport group in safe viewport.
    invoke-direct {{v0, v5}}, {SONG}->carVerticalOffset({GEOM})I
    move-result v1
    add-int v8, v8, v1
    add-int v10, v10, v1
    add-int v13, v13, v1
    add-int v15, v15, v1
    add-int v19, v19, v1
    add-int v24, v24, v1
    invoke-virtual {{v5}}, {GEOM}->getMediaHeight()I
    move-result v2
    add-int v14, v24, v2

'''
    body=once(body,anchor,code+anchor);text=text[:start]+body+text[end:]
    text+=fr'''

# E8 UI policy helpers; no account/network/DRM behavior.
.method private static carHideVolume({VOLUME})V
    .registers 2
    const/4 v0, 0x0
    invoke-virtual {{p0, v0}}, {VOLUME}->setPageVisible(Z)V
    const/16 v0, 0x8
    invoke-virtual {{p0, v0}}, Landroid/view/View;->setVisibility(I)V
    return-void
.end method

.method private final carVerticalOffset({GEOM})I
    .registers 8
    iget-object v0, p0, {SONG}->player:Landroid/view/ViewGroup;
    invoke-virtual {{v0}}, Landroid/view/View;->getHeight()I
    move-result v0
    iget v1, p0, {SONG}->insetBottom:I
    sub-int/2addr v0, v1
    iget v1, p0, {SONG}->insetTop:I
    invoke-virtual {{p1}}, {GEOM}->getThumbCenterY()I
    move-result v2
    invoke-virtual {{p1}}, {GEOM}->getThumbHeight()I
    move-result v3
    div-int/lit8 v3, v3, 0x2
    sub-int/2addr v2, v3
    invoke-virtual {{p1}}, {GEOM}->getMediaTop()I
    move-result v3
    invoke-virtual {{p1}}, {GEOM}->getMediaHeight()I
    move-result v4
    add-int/2addr v3, v4
    sub-int v4, v3, v2
    sub-int v5, v0, v1
    if-gt v4, v5, :e8_no_room
    add-int/2addr v0, v1
    sub-int/2addr v0, v2
    sub-int/2addr v0, v3
    div-int/lit8 v0, v0, 0x2
    return v0
    :e8_no_room
    const/4 v0, 0x0
    return v0
.end method
'''
    return text

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('knockout',type=Path);p.add_argument('song_column',type=Path);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    changes=[(a.knockout,patch_knockout(a.knockout.read_text(encoding='utf-8'))),(a.song_column,patch_song_column(a.song_column.read_text(encoding='utf-8')))]
    if not a.dry_run:
        if any(p.with_suffix('.smali.bak').exists() for p,_ in changes):raise ValueError('Backup already exists')
        for path,text in changes:
            with path.with_suffix('.smali.bak').open('xb') as f:f.write(path.read_bytes())
            path.write_text(text,encoding='utf-8',newline='\n')
    print('UI patches validated'+(' (dry run)' if a.dry_run else ' and applied'))
if __name__=='__main__':main()

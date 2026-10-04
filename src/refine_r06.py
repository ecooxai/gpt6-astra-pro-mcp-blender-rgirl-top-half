from pathlib import Path
p=Path('src/build_character.py');s=p.read_text()
assert '# Hair scalp and long layered guide locks.' in s
start=s.index('# Hair scalp and long layered guide locks.')
end=s.index('# Neutral portrait atelier lighting',start)
s=s[:start]+"# Original all-angle strand groom; no imported assets.\nexec((ROOT/'src'/'groom_v2.py').read_text(),globals())\n\n"+s[end:]
s=s.replace('(2.12,.375)','(2.12,.410)')
s=s.replace('y-=.014*exp(-(x/.145)**2-((z-2.142)/.07)**2)','y-=.042*exp(-(x/.145)**2-((z-2.142)/.07)**2)')
s=s.replace('y-=.112*exp(-(x/.080)**2-((z-2.785)/.22)**2)','y-=.082*exp(-(x/.078)**2-((z-2.785)/.22)**2)')
s=s.replace('y-=.176*exp(-(x/.093)**2-((z-2.567)/.080)**2)','y-=.126*exp(-(x/.096)**2-((z-2.567)/.073)**2)')
s=s.replace('y-=.070*exp(-((abs(x)-.083)/.041)**2-((z-2.533)/.044)**2)','y-=.056*exp(-((abs(x)-.083)/.043)**2-((z-2.533)/.044)**2)')
s=s.replace("scene.view_settings.look='AgX - Medium High Contrast'","scene.view_settings.look='AgX - Medium High Contrast'")
s=s.replace("area('Hair rim · broad strip',(1.8,1.4,4.6),300,(1,.83,.72),3.0)","rim=area('Hair rim · broad strip',(1.8,1.4,4.6),180,(.89,.92,1),3.4);rim.data.specular_factor=.5")
s=s.replace("scene.view_settings.exposure=.22","scene.view_settings.exposure=.10")
s=s.replace("scene.eevee.taa_render_samples=16\nCHAR", "scene.eevee.taa_render_samples=16\nif os.environ.get('FAST_PREVIEW')=='2':\n    scene.render.resolution_x=384;scene.render.resolution_y=512;scene.eevee.taa_render_samples=8\nCHAR")
# Correct tube winding for consistent outside-facing normals in Blender and glTF.
s=s.replace("fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))","fs.append((i*sides+j,(i+1)*sides+j,(i+1)*sides+(j+1)%sides,i*sides+(j+1)%sides))")
p.write_text(s)
print('R06_SOURCE_READY')

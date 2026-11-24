"""Actual Blender image decoding and Principled BSDF wiring of generated PBR maps."""
import bpy
import json
import sys
from pathlib import Path

def main():
    directory,output=map(Path,sys.argv[sys.argv.index("--")+1:])
    d=json.loads((directory/"materials.json").read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    images={}
    color_spaces={}
    for t in d["textures"]:
        image=bpy.data.images.load(str(directory/t["path"]),check_existing=False)
        # A full OCIO config offers Non-Color; Blender's minimal fallback
        # has only Linear and sRGB. Linear is identity for these RGB data maps.
        if t["color_space"]=="sRGB":
            image.colorspace_settings.name="sRGB"
        else:
            try:
                image.colorspace_settings.name="Non-Color"
            except TypeError:
                image.colorspace_settings.name="Linear"
        actual=image.colorspace_settings.name
        if actual not in (("sRGB",) if t["color_space"]=="sRGB" else ("Non-Color","Linear")):
            raise ValueError("unexpected image color space")
        color_spaces[t["id"]]=actual
        if tuple(image.size)!=(t["width"],t["height"]) or not image.has_data:
            # Force the actual decode before checking data.
            _=image.pixels[0]
        if tuple(image.size)!=(t["width"],t["height"]) or not image.has_data:
            raise ValueError("image decode failed")
        images[t["id"]]=image
    evidence=[]
    for spec in d["materials"]:
        m=bpy.data.materials.new(spec["id"])
        m.use_nodes=True
        tree=m.node_tree
        bsdf=next(n for n in tree.nodes if n.type=="BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value=spec["base_color"]
        bsdf.inputs["Metallic"].default_value=spec["metallic"]
        bsdf.inputs["Roughness"].default_value=spec["roughness"]
        for role in ("base_color","orm","normal"):
            node=tree.nodes.new("ShaderNodeTexImage")
            node.image=images[spec[role+"_texture"]]
            if role=="base_color":
                tree.links.new(node.outputs["Color"],bsdf.inputs["Base Color"])
            elif role=="orm":
                rgb=tree.nodes.new("ShaderNodeSeparateRGB")
                tree.links.new(node.outputs["Color"],rgb.inputs["Image"])
                tree.links.new(rgb.outputs["G"],bsdf.inputs["Roughness"])
                tree.links.new(rgb.outputs["B"],bsdf.inputs["Metallic"])
            else:
                normal=tree.nodes.new("ShaderNodeNormalMap")
                normal.space="TANGENT"
                normal.inputs["Strength"].default_value=spec["normal_scale"]
                tree.links.new(node.outputs["Color"],normal.inputs["Color"])
                tree.links.new(normal.outputs["Normal"],bsdf.inputs["Normal"])
        sockets=["Base Color","Metallic","Roughness","Normal"]
        if not all(bsdf.inputs[s].is_linked for s in sockets):
            raise ValueError("missing PBR link")
        evidence.append({"id":spec["id"],"linked":sockets})
    output.write_text(json.dumps({"version":bpy.app.version_string,"decoded_images":len(images),
                                  "materials":evidence,"color_spaces":color_spaces},sort_keys=True))

if __name__=="__main__":
    main()

# Page 2 layered Lumi reconstruction

Built-in imagegen was used with reference_current.png as the reference. New non-destructive asset: assets/oracle/lumi_reconstructed.png. The original lumi_base.png and reference artwork were not overwritten. No image-generation service is called by the app: the generated PNG is bundled and all runtime composition is local Tkinter.

Prompt specification: identity-preserving transparent extraction/reconstruction of only Panel 2 Lumi; remove witch hat and scarf, reconstruct concealed head/ears/neck, preserve seated pose, slight head tilt, cream fur, purple outline, pink cheeks and tail on viewer's left. Low-resolution pastel pixel art, no background, clothing, text or shadow. The generated character is approximate, not a recovery of original hidden pixels.

Integration: oracle_preview.update_oracle_preview reads the existing hat, buddy, accessory and selected_background state. It composites inside the existing preview frame, retains the original arrow pixels, holds persistent image references and updates one Canvas image. Existing wardrobe backgrounds and item sprites are reused. No Page 4 changes. None removes its category layer. Page 2 uses a reconstruction; all other pages retain their current art.

This supersedes the historical static-preview limitation in earlier repair reports. Final tests are recorded below.

Verification: 21 actual option clicks produced distinct preview images; None removes layers; one Canvas preview item; Back and disk-state restoration; Page 4 artwork hash unchanged. 28 unit tests and a fresh main.py reading/save/follow-up/new-reading flow passed. Original assets preserved.

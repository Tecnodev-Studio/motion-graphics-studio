# Publishing the video

- **Title**: concrete + curiosity, front-load the keyword, <= 70 chars; don't promise what the video doesn't show. Offer 3-5 options and say which you'd pick.
- **Hashtags**: 3-5 relevant ones; don't claim they are "trending" unless you saw a current source. **Description**: 2 lines + link/CTA. Put important links in the pinned comment.
- **Captions**: upload `captions.srt` (or `.vtt`) in the platform's caption tool; burned-in captions help silent viewers.
- **Thumbnail** (16:9): `python -m mgs stills project.py <t>` gives a frame; add big text with `K.title`.

## Getting the toolkit from GitHub
```bash
git clone https://github.com/Tecnodev-Studio/motion-graphics-studio.git
cd motion-graphics-studio
```
The workflow `.github/workflows/ci.yml` runs the self-test on every push. Releases: create one on GitHub and attach the zip.

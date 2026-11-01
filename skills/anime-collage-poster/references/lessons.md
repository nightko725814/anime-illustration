# Decision log (2026-10-26 → 10-30)

What was tried on the reference machine, what the feedback said, and what stuck. Read this before proposing a direction that testing already rejected.

## Getting the look

1. **The first Teto pick (v2, seed 20261026)** was two passes: 1536×864, then 1920×1088 at 0.4, 8 steps euler. Later rounds "fixed" traits the user hadn't flagged, and the user said "越训练越差了". From then on: freeze picks, change one thing at a time, ask which result is closest.
2. **The reference poster's real recipe** came from its PNG metadata. Dragging the image into ComfyUI shows it too.
   - The recipe: RedCraft 2.0 + z3zz4 0.55 + ba_style (BArtstyle V1) 0.75, a ~1900-word brief, 1920×1080 single pass, 10 steps er_sde.
   - The pack's `@artist` CR Text node was never connected.
   - The canvas shows stale prompts: the WeiLin editor cache and the ShowText display. Only the `positive` field is encoded.
3. **Long brief vs short prompt.** Swapping a 250-word prompt for the 2000-word brief was the biggest single jump toward the reference.
4. **RedCraft 3.0 INT4** brought back texture and chaos, but put paint flecks on faces and lost the titles. BArtstyle V1 at 0.75 kept faces clean; V2 closed eyes and fragmented faces.
5. **Calm-background brief:** the result was washed out and pinkish, and the user said "方向不对".
6. **Stacking three LoRAs** on RedCraft INT4 turned one image into noise.
7. **Official Turbo + z3zz4 0.95** gave clean, structured posters with readable titles. That became the recipe. Background clutter had come from the RedCraft base, not from the prompt.
8. **Front light.** The user said "人物正面缺少高光":
   - Low-denoise img2img (0.35 / 0.5) kept the layout but barely changed the light.
   - Text-to-image with a new lighting paragraph re-laid out everything, but the user picked it ("文生图补光版更好").

## Cleaning up (mostly rejected)

9. **Cutout + clean background + real-font typesetting:**
   - The user first asked "补齐下半身", because the background band cut the character at the waist.
   - Then: "文字太过板正", "左边颜色单一 太空 没有碎片感".
   - A rich-collage background with a horizontal title was better.
   - The user still ended with "就这种感觉算了吧" and kept the raw image.
10. **Cutout tools:** SAM 2.1 (whole-character box plus points) produced clean full-body masks. anime-seg failed on same-color hair and on collage scraps.

## Nira-chan series

11. **References first.**
    - My first guess was a short bob. Then the user's references showed a classic long-hair look.
    - Then the user specified a short bob and hoodie, "不要长头发", "朝气一点", a hedgehog instead of the cat, and the logo hoodie.
    - "生姜" was a pale-pink cat from the 海馬成長痛 MV, not a ginger tabby.
12. **Style.**
    - ZUTOMAYO-MV flat style worked technically, but the user wanted "按生成 teto 的流程，画风也和 teto 一样".
    - Then "更帅更痞，像 Teto 那样": a look back over the shoulder with a hand in the hair.
13. **Chinese-girl variant.**
    - Bubble gum and xiaolongbao, with 香辛龍 concert motifs, then "紫黑中华风".
    - Long hair under the buns would not go away, and the user accepted it.
    - No full render drew the bubble gum, so a local inpaint (seed 202) added it.
14. **Fixes the user asked for on the hoodie pick:**
    - 断夜中 → 真夜中: a real-font replacement, 3,246 px changed.
    - "右手大拇指很怪" → "直接把虎口的那坨去掉": masked only the blob and prompted it as hair. A whole-hand redraw had erased the hand.
15. **Text with extra characters** in the purple-black poster: the user stopped the fix midway and saved the image as-is.

## Operations

16. **Memory.** Queueing many different jobs ran RAM down to 1.7 GB free, and one inpaint took 30 minutes. Fix: `POST /free`, then fewer concurrent different jobs.
17. **Queue hygiene.**
    - Stopping a shell loop leaves its submitted ComfyUI job in the queue.
    - An `/interrupt` once killed a wanted job, because a different job had just started.
    - Check `/queue` by SaveImage prefix, delete pending jobs by id, and use `--front` for urgent fixes.
18. **Keep picks bit-exact.** All picks are frozen with metadata-derived workflows, and re-renders reproduce them pixel for pixel (100%, max diff 0).

## First test of the skills (2026-10-30, user verdicts pending)

19. **Teto × vintage British posters + paper flowers.** One seed, because the user asked for one image ("试画一张").
    - The paragraph-by-paragraph adaptation worked: every British motif, the baguette and the teacup appeared, and the palette stayed vivid.
    - Misses: the paper flowers came out as painted roses, the title sat at the top center, and a few labels were garbled.
20. **Adachi Rei with an opened stomach and broken wires, one image per skill** ("足立零肚子露出破损电线 用两个skill分别画一张").
    - Identity: built from Moegirl's description of her official UTAU design. It was right in both images.
    - Damage, short illustration prompt: kept only a small gap at the belt, plus sparks on a wire in her hand.
    - Damage, 2,500-word poster brief: dropped completely, even though the brief named it in four paragraphs.
    - So must-have details in posters need a planned local fix after the pick, like the bubble gum.
21. **Speed under low RAM.**
    - About 2.6 GB was free at the start: Claude, Codex, ChatGPT and QQ were open.
    - Three back-to-back renders took 328 s, 461 s and 1,046 s.
    - `POST /free` afterwards brought free RAM back to 7.5 GB. When RAM is that tight, unload between renders.
22. **Hands.**
    - After seeing both Adachi Rei images side by side, the user said "手有点不行". I queued fixes for all four hands.
    - The user then clarified: "左边的是对的 右边的手不对". Only the poster was wrong, so the illustration jobs had to be cancelled.
    - So when feedback could apply to several images on screen, confirm which one before queueing renders.
    - The poster fix: the plug hand came from seed 44 at denoise 0.65 and the bottom hand from seed 202 at 0.8. Seed 202 at 0.8 had erased the plug hand.

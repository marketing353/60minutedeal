# -*- coding: utf-8 -*-
"""Generate ram-jeep-dodge-chrysler.html from index.html.

Keeps the head (tracking), header, the <section id="request"> form, the footer
and the whole x-dc component script verbatim, and replaces only the marketing
sections. The wizard, Meta/Google tags, ADF delivery and /thank-you redirect are
therefore identical to the main page and cannot drift.

    python tools/make-cdjr.py
"""
import io
import re
import sys

URL = "https://usedcarssimivalley.com/ram-jeep-dodge-chrysler"
TITLE = "Ram, Jeep, Dodge & Chrysler — No Add-Ons, No Games, Straight-Up Pricing"
DESC = ("Ram, Jeep, Dodge and Chrysler with no dealer add-ons and no bait-and-switch. "
        "Tell us what you want in 60 seconds and get the real number in writing before "
        "you drive over. Trade-ins welcome. No credit check.")

# Everything from <section id="hero"> up to (not including) the form.
TOP = """<section id="hero" style="background:#0d1a13;color:#eef4ea;overflow:hidden">
  <div style="max-width:1120px;margin:0 auto;padding:44px 20px 56px;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:44px;align-items:center">
    <div>
      <div style="display:inline-flex;align-items:center;gap:8px;font-family:'Geist Mono',monospace;font-size:11.5px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#cfe0c9;border:1px solid rgba(214,255,56,.3);background:rgba(214,255,56,.08);padding:7px 12px;border-radius:100px">
        <span style="width:6px;height:6px;border-radius:50%;background:#d6ff38"></span>Ram · Jeep · Dodge · Chrysler
      </div>
      <h1 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:clamp(44px,10.5vw,84px);line-height:.94;letter-spacing:-.045em;margin:22px 0 20px;color:#fff;text-wrap:balance">No add-ons. No games. <span style="background:#d6ff38;color:#0d1a13;padding:0 .12em;border-radius:.1em">Just the price.</span></h1>
      <p style="font-size:clamp(17px,4.4vw,19px);line-height:1.55;color:#b7c9b6;margin:0 0 24px;max-width:540px;text-wrap:pretty">Tell us what you want in <b style="color:#fff">60 seconds</b>. We send back real Ram, Jeep, Dodge and Chrysler vehicles with the real number — and that number is the one you pay when you arrive.</p>
      <div style="display:flex;flex-direction:column;gap:12px;max-width:420px">
        <a href="#request" style="display:flex;align-items:center;justify-content:center;gap:10px;min-height:56px;padding:0 24px;border-radius:12px;background:#d6ff38;color:#0d1a13;text-decoration:none;font-weight:700;font-size:16px">Get my straight-up price — free ↗</a>
        <a href="#addons" style="display:flex;align-items:center;justify-content:center;min-height:48px;color:#cfe0c9;font-size:14.5px;font-weight:500;text-decoration:none;border:1px solid #2a4434;border-radius:12px">See exactly what we don't charge for ↓</a>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:22px;font-size:13.5px;color:#cfe0c9">
        <span style="display:flex;gap:7px"><span style="color:#d6ff38">✓</span>No dealer add-ons</span>
        <span style="display:flex;gap:7px"><span style="color:#d6ff38">✓</span>Trade-ins welcome</span>
        <span style="display:flex;gap:7px"><span style="color:#d6ff38">✓</span>No credit check</span>
        <span style="display:flex;gap:7px"><span style="color:#d6ff38">✓</span>No bait-and-switch</span>
      </div>
    </div>

    <div style="background:#f5f8ef;color:#0d1a13;border-radius:20px;padding:24px 22px;box-shadow:0 24px 60px rgba(0,0,0,.35)">
      <div style="display:flex;justify-content:space-between;align-items:center;font-family:'Geist Mono',monospace;font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#5c6b61">
        <span>Your quote · example</span><span style="color:#4c6410">In writing</span>
      </div>
      <div style="height:1px;background:#d3dccb;margin:14px 0"></div>
      <div style="display:flex;justify-content:space-between;gap:16px;padding:8px 0;font-size:15px"><span style="color:#5c6b61">Vehicle price</span><b>$38,900</b></div>
      <div style="display:flex;justify-content:space-between;gap:16px;padding:8px 0;font-size:15px"><span style="color:#5c6b61">Dealer add-ons</span><b style="color:#4c6410">$0</b></div>
      <div style="display:flex;justify-content:space-between;gap:16px;padding:8px 0;font-size:15px"><span style="color:#5c6b61">“Market adjustment”</span><b style="color:#4c6410">$0</b></div>
      <div style="display:flex;justify-content:space-between;gap:16px;padding:8px 0;font-size:15px"><span style="color:#5c6b61">Your trade-in</span><b>Valued up front</b></div>
      <div style="height:1px;background:#d3dccb;margin:14px 0"></div>
      <div style="display:flex;justify-content:space-between;gap:16px;font-size:16px"><b>What you pay</b><b style="background:#d6ff38;padding:2px 8px;border-radius:6px">The number we quoted</b></div>
      <p style="margin:14px 0 0;font-size:12px;color:#5c6b61">Illustrative example. Tax, title, licence and documentation fees are set by law and shown separately.</p>
    </div>
  </div>
</section>

<section style="background:#f5f8ef;scroll-margin-top:64px">
  <div style="max-width:1120px;margin:0 auto;padding:64px 20px 56px">
    <div style="font-family:'Geist Mono',monospace;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#4c6410">The whole promise</div>
    <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:clamp(30px,7.4vw,46px);line-height:1.04;letter-spacing:-.035em;margin:12px 0 10px">Four things we won't do to you.</h2>
    <p style="margin:0 0 30px;font-size:16px;color:#5c6b61;max-width:620px">Everything below is the part of car buying people actually dread. We took it out.</p>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:14px">
      <div style="background:#fff;border-radius:16px;padding:22px 20px">
        <div style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:19px;margin-bottom:8px">No dealer add-ons</div>
        <p style="margin:0;font-size:14.5px;line-height:1.55;color:#5c6b61">No paint sealant, no nitrogen in the tyres, no VIN etching, no pinstripe package you never asked for. Not pre-installed, not “already on the car”, not negotiable down from a number we invented.</p>
      </div>
      <div style="background:#fff;border-radius:16px;padding:22px 20px">
        <div style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:19px;margin-bottom:8px">No bait-and-switch</div>
        <p style="margin:0;font-size:14.5px;line-height:1.55;color:#5c6b61">The vehicle we quote is a vehicle we have. If it sells before you get here, we tell you straight away — we don't let you drive over and then walk you to something pricier.</p>
      </div>
      <div style="background:#fff;border-radius:16px;padding:22px 20px">
        <div style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:19px;margin-bottom:8px">No surprise line items</div>
        <p style="margin:0;font-size:14.5px;line-height:1.55;color:#5c6b61">One number, in writing, before you drive over. Tax, title, licence and documentation fees are set by law — we show them separately so you can see exactly what is ours and what isn't.</p>
      </div>
      <div style="background:#fff;border-radius:16px;padding:22px 20px">
        <div style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:19px;margin-bottom:8px">Trade-ins valued up front</div>
        <p style="margin:0;font-size:14.5px;line-height:1.55;color:#5c6b61">Tell us what you're driving now and we put a number on it before you commit to anything — not after you've already fallen for the new one.</p>
      </div>
    </div>
  </div>
</section>

<section id="addons" style="background:#0d1a13;color:#eef4ea;scroll-margin-top:64px">
  <div style="max-width:1120px;margin:0 auto;padding:64px 20px 56px">
    <div style="font-family:'Geist Mono',monospace;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#d6ff38">The add-on math</div>
    <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:clamp(30px,7.4vw,46px);line-height:1.04;letter-spacing:-.035em;margin:12px 0 10px;color:#fff">What a “great deal” usually hides.</h2>
    <p style="margin:0 0 30px;font-size:16px;color:#b7c9b6;max-width:640px">These are the extras commonly added to a window sticker across the industry. Ranges are typical, not ours — because ours is the last row.</p>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:14px">
      <div style="border:1px solid #2a4434;border-radius:16px;overflow:hidden">
        <div style="padding:14px 18px;background:rgba(255,255,255,.04);font-weight:700;font-size:15px;color:#fff">Typical dealer add-ons</div>
        <div style="display:flex;justify-content:space-between;gap:16px;padding:13px 18px;border-top:1px solid #1d3327;font-size:14.5px"><span style="color:#cfe0c9">Paint &amp; fabric protection</span><span style="color:#fff;font-weight:600">$600–$1,500</span></div>
        <div style="display:flex;justify-content:space-between;gap:16px;padding:13px 18px;border-top:1px solid #1d3327;font-size:14.5px"><span style="color:#cfe0c9">Nitrogen-filled tyres</span><span style="color:#fff;font-weight:600">$200–$400</span></div>
        <div style="display:flex;justify-content:space-between;gap:16px;padding:13px 18px;border-top:1px solid #1d3327;font-size:14.5px"><span style="color:#cfe0c9">VIN etching</span><span style="color:#fff;font-weight:600">$200–$400</span></div>
        <div style="display:flex;justify-content:space-between;gap:16px;padding:13px 18px;border-top:1px solid #1d3327;font-size:14.5px"><span style="color:#cfe0c9">Door edge guards &amp; pinstripes</span><span style="color:#fff;font-weight:600">$300–$800</span></div>
        <div style="display:flex;justify-content:space-between;gap:16px;padding:13px 18px;border-top:1px solid #1d3327;font-size:14.5px"><span style="color:#cfe0c9">“Market adjustment”</span><span style="color:#fff;font-weight:600">Anything they like</span></div>
      </div>
      <div style="border:1px solid #d6ff38;border-radius:16px;overflow:hidden;background:rgba(214,255,56,.06);display:flex;flex-direction:column;justify-content:center;padding:28px 22px">
        <div style="font-family:'Geist Mono',monospace;font-size:11.5px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#d6ff38">Our add-on total</div>
        <div style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:clamp(56px,16vw,96px);line-height:1;letter-spacing:-.04em;color:#d6ff38;margin:10px 0 12px">$0</div>
        <p style="margin:0;font-size:15px;line-height:1.55;color:#cfe0c9">Every time. On every Ram, Jeep, Dodge and Chrysler we quote. If you ever see an add-on line on a quote from us, you don't have to pay it.</p>
      </div>
    </div>
  </div>
</section>

"""

# Everything after the form, up to </main>.
BOTTOM = """
<section style="background:#fff">
  <div style="max-width:1120px;margin:0 auto;padding:64px 20px 56px">
    <div style="font-family:'Geist Mono',monospace;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#4c6410">Four brands</div>
    <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:clamp(30px,7.4vw,46px);line-height:1.04;letter-spacing:-.035em;margin:12px 0 10px">Ram, Jeep, Dodge, Chrysler. That's it.</h2>
    <p style="margin:0 0 30px;font-size:16px;color:#5c6b61;max-width:620px">We stay in our lane. Four brands, known properly, instead of a bit of everything.</p>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:14px">
      <div style="background:#f5f8ef;border-radius:16px;padding:22px 20px">
        <div style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:22px;letter-spacing:-.02em">Ram</div>
        <p style="margin:8px 0 0;font-size:14.5px;line-height:1.55;color:#5c6b61">1500 through 3500. Work trucks, tow rigs and the one that doubles as the family car on weekends.</p>
      </div>
      <div style="background:#f5f8ef;border-radius:16px;padding:22px 20px">
        <div style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:22px;letter-spacing:-.02em">Jeep</div>
        <p style="margin:8px 0 0;font-size:14.5px;line-height:1.55;color:#5c6b61">Wrangler, Grand Cherokee, Gladiator. For getting out of town, and for the school run in between.</p>
      </div>
      <div style="background:#f5f8ef;border-radius:16px;padding:22px 20px">
        <div style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:22px;letter-spacing:-.02em">Dodge</div>
        <p style="margin:8px 0 0;font-size:14.5px;line-height:1.55;color:#5c6b61">Charger, Durango, Hornet. Room for everyone, with more under the hood than the neighbours expect.</p>
      </div>
      <div style="background:#f5f8ef;border-radius:16px;padding:22px 20px">
        <div style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:22px;letter-spacing:-.02em">Chrysler</div>
        <p style="margin:8px 0 0;font-size:14.5px;line-height:1.55;color:#5c6b61">Pacifica and 300. The quiet, comfortable end — minivans that don't feel like a compromise.</p>
      </div>
    </div>
  </div>
</section>

<section style="background:#f5f8ef">
  <div style="max-width:1120px;margin:0 auto;padding:60px 20px">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:32px;align-items:center">
      <div>
        <div style="font-family:'Geist Mono',monospace;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#4c6410">Trade-ins</div>
        <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:clamp(28px,6.5vw,40px);line-height:1.05;letter-spacing:-.035em;margin:12px 0 12px">Bring what you're driving now.</h2>
        <p style="margin:0 0 16px;font-size:16px;line-height:1.6;color:#5c6b61">Most people find out what their car is worth at the very end, once they're already attached to the new one. That's not an accident — it's when you'll argue least.</p>
        <p style="margin:0;font-size:16px;line-height:1.6;color:#5c6b61">Tell us about your trade-in on the form and we put a number on it <b style="color:#0d1a13">before</b> you're standing in the showroom. Still owe on it? That's normal. Say so and we'll work it into the figure.</p>
      </div>
      <div style="background:#0d1a13;color:#eef4ea;border-radius:18px;padding:26px 22px">
        <div style="font-family:'Geist Mono',monospace;font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#d6ff38">What we need</div>
        <ul style="list-style:none;margin:14px 0 0;padding:0;display:flex;flex-direction:column;gap:12px;font-size:15px">
          <li style="display:flex;gap:10px"><span style="color:#d6ff38">✓</span>Year, make and model</li>
          <li style="display:flex;gap:10px"><span style="color:#d6ff38">✓</span>Rough mileage</li>
          <li style="display:flex;gap:10px"><span style="color:#d6ff38">✓</span>Whether there's still a loan on it</li>
          <li style="display:flex;gap:10px"><span style="color:#d6ff38">✓</span>Anything obviously wrong with it</li>
        </ul>
        <p style="margin:16px 0 0;font-size:13px;color:#a8bda6">Final value depends on an in-person appraisal — condition, mileage and history. We'd rather give you a real range now than a flattering one that shrinks later.</p>
      </div>
    </div>
  </div>
</section>

<section style="background:#fff">
  <div style="max-width:1120px;margin:0 auto;padding:60px 20px 50px">
    <div style="font-family:'Geist Mono',monospace;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#4c6410;text-align:center">Real customers</div>
    <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:clamp(28px,6.5vw,40px);line-height:1.05;letter-spacing:-.035em;margin:12px 0 26px;text-align:center">Unedited, straight from the comments.</h2>
    <div style="columns:1;column-gap:14px" class="cdjr-wall">
      <img loading="lazy" decoding="async" width="1000" height="334" src="./img/testimonials/testimonial-03.webp" alt="Customer comment about 60 Minute Car Deals" style="display:block;width:100%;height:auto;margin:0 0 14px;border-radius:12px;background:#f5f8ef;break-inside:avoid">
      <img loading="lazy" decoding="async" width="1000" height="810" src="./img/testimonials/testimonial-21.webp" alt="Customer comment about 60 Minute Car Deals" style="display:block;width:100%;height:auto;margin:0 0 14px;border-radius:12px;background:#f5f8ef;break-inside:avoid">
      <img loading="lazy" decoding="async" width="1000" height="516" src="./img/testimonials/testimonial-09.webp" alt="Customer comment about 60 Minute Car Deals" style="display:block;width:100%;height:auto;margin:0 0 14px;border-radius:12px;background:#f5f8ef;break-inside:avoid">
      <img loading="lazy" decoding="async" width="1000" height="334" src="./img/testimonials/testimonial-19.webp" alt="Customer comment about 60 Minute Car Deals" style="display:block;width:100%;height:auto;margin:0 0 14px;border-radius:12px;background:#f5f8ef;break-inside:avoid">
      <img loading="lazy" decoding="async" width="1000" height="455" src="./img/testimonials/testimonial-14.webp" alt="Customer comment about 60 Minute Car Deals" style="display:block;width:100%;height:auto;margin:0 0 14px;border-radius:12px;background:#f5f8ef;break-inside:avoid">
      <img loading="lazy" decoding="async" width="1000" height="760" src="./img/testimonials/testimonial-33.webp" alt="Customer comment about 60 Minute Car Deals" style="display:block;width:100%;height:auto;margin:0 0 14px;border-radius:12px;background:#f5f8ef;break-inside:avoid">
      <img loading="lazy" decoding="async" width="1000" height="333" src="./img/testimonials/testimonial-20.webp" alt="Customer comment about 60 Minute Car Deals" style="display:block;width:100%;height:auto;margin:0 0 14px;border-radius:12px;background:#f5f8ef;break-inside:avoid">
      <img loading="lazy" decoding="async" width="1000" height="516" src="./img/testimonials/testimonial-29.webp" alt="Customer comment about 60 Minute Car Deals" style="display:block;width:100%;height:auto;margin:0 0 14px;border-radius:12px;background:#f5f8ef;break-inside:avoid">
    </div>
    <p style="margin:6px 0 0;font-size:12px;color:#5c6b61;text-align:center">Comments posted publicly by customers, shown unedited.</p>
  </div>
</section>

<section id="faq" style="background:#f5f8ef;scroll-margin-top:64px">
  <div style="max-width:800px;margin:0 auto;padding:64px 20px 56px">
    <div style="font-family:'Geist Mono',monospace;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#4c6410">Straight answers</div>
    <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:clamp(30px,7.4vw,46px);line-height:1.04;letter-spacing:-.035em;margin:12px 0 24px">The questions worth asking.</h2>
    <details style="border-bottom:1px solid #d3dccb">
      <summary style="list-style:none;cursor:pointer;display:flex;justify-content:space-between;gap:16px;align-items:center;min-height:60px;padding:14px 0;font-weight:600;font-size:16.5px">What exactly counts as a “dealer add-on”?<span style="color:#5c6b61;font-size:22px;font-weight:400">+</span></summary>
      <p style="margin:0 0 18px;font-size:15px;line-height:1.6;color:#5c6b61">Anything added by the dealership rather than the manufacturer, charged on top of the vehicle price: paint and fabric protection, nitrogen in the tyres, VIN etching, pinstripes, door guards, theft-protection packages, and “market adjustment”. We don't add them. Tax, title, licence and documentation fees are different — those are set by law and we show them as separate lines.</p>
    </details>
    <details style="border-bottom:1px solid #d3dccb">
      <summary style="list-style:none;cursor:pointer;display:flex;justify-content:space-between;gap:16px;align-items:center;min-height:60px;padding:14px 0;font-weight:600;font-size:16.5px">How do I know the vehicle is actually there?<span style="color:#5c6b61;font-size:22px;font-weight:400">+</span></summary>
      <p style="margin:0 0 18px;font-size:15px;line-height:1.6;color:#5c6b61">Because we quote from what we have, not from an advert. Cars do sell while people are deciding — if that happens we tell you before you set off, and we tell you what else genuinely fits instead. What we won't do is get you through the door and then start steering you somewhere more expensive.</p>
    </details>
    <details style="border-bottom:1px solid #d3dccb">
      <summary style="list-style:none;cursor:pointer;display:flex;justify-content:space-between;gap:16px;align-items:center;min-height:60px;padding:14px 0;font-weight:600;font-size:16.5px">Does the form affect my credit?<span style="color:#5c6b61;font-size:22px;font-weight:400">+</span></summary>
      <p style="margin:0 0 18px;font-size:15px;line-height:1.6;color:#5c6b61">No. Nothing on this form runs a credit check of any kind. The credit questions are estimates so we can point you at realistic numbers. An actual finance application is a separate step that needs your explicit authorisation.</p>
    </details>
    <details style="border-bottom:1px solid #d3dccb">
      <summary style="list-style:none;cursor:pointer;display:flex;justify-content:space-between;gap:16px;align-items:center;min-height:60px;padding:14px 0;font-weight:600;font-size:16.5px">Can I still trade in if I owe money on my car?<span style="color:#5c6b61;font-size:22px;font-weight:400">+</span></summary>
      <p style="margin:0 0 18px;font-size:15px;line-height:1.6;color:#5c6b61">Yes, and it's extremely common. Tell us on the form and we'll factor the outstanding balance into the figures rather than springing it on you later. If you owe more than it's worth, we'll say so plainly and show you what that means.</p>
    </details>
    <details style="border-bottom:1px solid #d3dccb">
      <summary style="list-style:none;cursor:pointer;display:flex;justify-content:space-between;gap:16px;align-items:center;min-height:60px;padding:14px 0;font-weight:600;font-size:16.5px">Will someone start phoning me?<span style="color:#5c6b61;font-size:22px;font-weight:400">+</span></summary>
      <p style="margin:0 0 18px;font-size:15px;line-height:1.6;color:#5c6b61">Not until you ask. You get your numbers by email first. If you'd rather talk it through, say so and we'll call — otherwise we won't.</p>
    </details>
  </div>
</section>

<section style="background:#0d1a13;color:#fff;text-align:center">
  <div style="max-width:760px;margin:0 auto;padding:64px 20px 72px">
    <h2 style="font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:clamp(30px,8vw,52px);line-height:1.02;letter-spacing:-.04em;margin:0 0 14px;text-wrap:balance">Get the real number first.</h2>
    <p style="margin:0 0 26px;font-size:16.5px;line-height:1.6;color:#b7c9b6">Sixty seconds now, and you'll know what a Ram, Jeep, Dodge or Chrysler actually costs you — before anyone tries to add to it.</p>
    <a href="#request" style="display:flex;align-items:center;justify-content:center;min-height:56px;max-width:380px;margin:0 auto;border-radius:12px;background:#d6ff38;color:#0d1a13;text-decoration:none;font-weight:700;font-size:16px">Get my straight-up price ↗</a>
  </div>
</section>
"""


def build(src):
    out = src

    # --- head -------------------------------------------------------------
    out = re.sub(r"<title>[^<]*</title>", "<title>%s</title>" % TITLE, out, count=1)
    out = re.sub(r'(<meta name="description" content=")[^"]*(">)',
                 lambda m: m.group(1) + DESC + m.group(2), out, count=1)
    out = re.sub(r'(<meta property="og:title" content=")[^"]*(">)',
                 lambda m: m.group(1) + TITLE + m.group(2), out, count=1)
    out = re.sub(r'(<meta property="og:description" content=")[^"]*(">)',
                 lambda m: m.group(1) + DESC + m.group(2), out, count=1)
    out = re.sub(r'(<meta name="twitter:title" content=")[^"]*(">)',
                 lambda m: m.group(1) + TITLE + m.group(2), out, count=1)
    out = re.sub(r'(<meta name="twitter:description" content=")[^"]*(">)',
                 lambda m: m.group(1) + DESC + m.group(2), out, count=1)
    out = re.sub(r'<link rel="canonical" href="[^"]*">',
                 '<link rel="canonical" href="%s">' % URL, out, count=1)
    out = re.sub(r'<meta property="og:url" content="[^"]*">',
                 '<meta property="og:url" content="%s">' % URL, out, count=1)

    # No Spanish variant of this page yet, so the alternates would be wrong.
    out = re.sub(r'\n<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', out)

    # Same reason: the switcher would send people to a different page entirely.
    out = re.sub(r'\s*<a href="/es" hreflang="es" lang="es"[^>]*>[^<]*</a>', '', out, count=1)

    # Multi-column testimonial wall needs its breakpoints in the helmet CSS.
    out = out.replace(
        "@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}",
        "@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}\n"
        "@media(min-width:720px){.cdjr-wall{columns:2!important}}\n"
        "@media(min-width:1080px){.cdjr-wall{columns:3!important}}", 1)

    # Trademark notice — the page names four marques but identifies no dealer.
    out = out.replace(
        "This website is not affiliated with or endorsed by Meta or Facebook.",
        "Ram, Jeep, Dodge and Chrysler are registered trademarks of FCA US LLC. "
        "This website is independent and is not affiliated with, endorsed by or "
        "sponsored by FCA US LLC, Stellantis, Meta or Facebook.")

    # --- body -------------------------------------------------------------
    i_hero = out.index('<section id="hero"')
    i_form = out.index('<section id="request"')
    form_end = out.index('</section>', i_form) + len('</section>')
    i_main_end = out.index('</main>')

    out = out[:i_hero] + TOP + out[i_form:form_end] + BOTTOM + out[i_main_end:]
    return out


def main():
    src = io.open('index.html', encoding='utf-8').read()
    for marker in ('<section id="hero"', '<section id="request"', '</main>',
                   '<link rel="canonical"', '<title>'):
        if marker not in src:
            print("ERROR: index.html no longer contains %r" % marker)
            return 1
    out = build(src)
    io.open('ram-jeep-dodge-chrysler.html', 'w', encoding='utf-8', newline='\n').write(out)
    print("ram-jeep-dodge-chrysler.html written (%d KB)" % (len(out.encode('utf-8')) // 1024))
    return 0


if __name__ == '__main__':
    sys.exit(main())

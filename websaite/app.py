from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from pathlib import Path

app = FastAPI()

# 静态文件 & 模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 数据文件
PRODUCTS_PATH = Path("data/products.json")
SECTIONS_PATH = Path("data/sections.json")


# ----------------------------
# JSON 读写工具函数
# ----------------------------
def _ensure_json_file(path: Path, default_text: str = "[]"):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(default_text, encoding="utf-8")


def load_products():
    _ensure_json_file(PRODUCTS_PATH, "[]")
    return json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))


def save_products(products):
    PRODUCTS_PATH.write_text(
        json.dumps(products, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_sections():
    _ensure_json_file(SECTIONS_PATH, "[]")
    return json.loads(SECTIONS_PATH.read_text(encoding="utf-8"))


def save_sections(sections):
    SECTIONS_PATH.write_text(
        json.dumps(sections, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def slugify(s: str) -> str:
    """
    简单生成一个 id（用于 URL）
    只保留字母数字和 -，中文就直接用 p + 数字方案更稳
    """
    s = (s or "").strip().lower()
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
        elif ch in [" ", "_", "-"]:
            out.append("-")
    slug = "".join(out).strip("-")
    return slug or ""


# =========================================================
# ✅ 这里就是你要的 home() ：首页路由
# =========================================================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    products = load_products()
    sections = load_sections()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "我的第一个 Python 网页",
            "subtitle": "FastAPI + Jinja2 正在运行",
            "products": products,
            "sections": sections,  # ✅ 图文模块动态数据
        },
    )


# ----------------------------
# 产品后台（products）
# ----------------------------
@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    products = load_products()
    return templates.TemplateResponse("admin.html", {"request": request, "products": products})


@app.post("/admin/add")
def admin_add(
    title: str = Form(...),
    desc: str = Form(...),
    price: int = Form(...),
    tag: str = Form(""),
    badge: str = Form(""),
    link: str = Form("#"),
):
    products = load_products()

    # 生成 id：如果你已有 slug（比如 ppt-year-end），也可以在这里自定义
    pid = f"p{len(products)+1}"
    products.append(
        {
            "id": pid,
            "tag": tag,
            "title": title,
            "desc": desc,
            "price": price,
            "badge": badge,
            "link": link,
        }
    )
    save_products(products)
    return RedirectResponse("/admin", status_code=303)


@app.get("/admin/edit/{pid}", response_class=HTMLResponse)
def admin_edit(request: Request, pid: str):
    products = load_products()
    product = next((p for p in products if p.get("id") == pid), None)
    if not product:
        return RedirectResponse("/admin", status_code=303)

    return templates.TemplateResponse("admin_edit.html", {"request": request, "product": product})


@app.post("/admin/edit")
def admin_edit_save(
    pid: str = Form(...),
    title: str = Form(...),
    desc: str = Form(...),
    price: int = Form(...),
    tag: str = Form(""),
    badge: str = Form(""),
    link: str = Form("#"),
):
    products = load_products()
    for p in products:
        if p.get("id") == pid:
            p.update(
                {
                    "title": title,
                    "desc": desc,
                    "price": price,
                    "tag": tag,
                    "badge": badge,
                    "link": link,
                }
            )
            break

    save_products(products)
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/delete")
def admin_delete(pid: str = Form(...)):
    products = load_products()
    products = [p for p in products if p.get("id") != pid]
    save_products(products)
    return RedirectResponse("/admin", status_code=303)


# ----------------------------
# 图文模块后台（sections）
# ----------------------------
@app.get("/admin/sections", response_class=HTMLResponse)
def admin_sections(request: Request):
    sections = load_sections()
    return templates.TemplateResponse("admin_sections.html", {"request": request, "sections": sections})


@app.post("/admin/sections/add")
def admin_sections_add(
    title: str = Form(...),
    desc: str = Form(...),
    bullets: str = Form(""),
    image: str = Form(""),
    reverse: str = Form("0"),
):
    """
    bullets：用英文逗号 , 分隔（或你自己在前端做多行输入也行）
    reverse：0/1
    """
    sections = load_sections()

    sid = f"s{len(sections)+1}"
    bullet_list = [x.strip() for x in bullets.split(",") if x.strip()]
    sections.append(
        {
            "id": sid,
            "title": title,
            "desc": desc,
            "bullets": bullet_list,
            "image": image or "/static/img/illus1.png",
            "reverse": True if reverse == "1" else False,
        }
    )
    save_sections(sections)
    return RedirectResponse("/admin/sections", status_code=303)


@app.get("/admin/sections/edit/{sid}", response_class=HTMLResponse)
def admin_sections_edit(request: Request, sid: str):
    sections = load_sections()
    sec = next((s for s in sections if s.get("id") == sid), None)
    if not sec:
        return RedirectResponse("/admin/sections", status_code=303)

    # bullets 转成字符串，方便编辑
    bullets_str = ", ".join(sec.get("bullets", []))
    return templates.TemplateResponse(
        "admin_sections_edit.html",
        {"request": request, "section": sec, "bullets_str": bullets_str},
    )


@app.post("/admin/sections/edit")
def admin_sections_edit_save(
    sid: str = Form(...),
    title: str = Form(...),
    desc: str = Form(...),
    bullets: str = Form(""),
    image: str = Form(""),
    reverse: str = Form("0"),
):
    sections = load_sections()
    bullet_list = [x.strip() for x in bullets.split(",") if x.strip()]

    for s in sections:
        if s.get("id") == sid:
            s.update(
                {
                    "title": title,
                    "desc": desc,
                    "bullets": bullet_list,
                    "image": image or s.get("image", ""),
                    "reverse": True if reverse == "1" else False,
                }
            )
            break

    save_sections(sections)
    return RedirectResponse("/admin/sections", status_code=303)


@app.post("/admin/sections/delete")
def admin_sections_delete(sid: str = Form(...)):
    sections = load_sections()
    sections = [s for s in sections if s.get("id") != sid]
    save_sections(sections)
    return RedirectResponse("/admin/sections", status_code=303)

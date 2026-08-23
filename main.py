# =====================================================================
# 🐍 TikTok USA 24/7 Session Keeper & Universal Country Inspector
# دعم إظهار الدول الحقيقية باللغة العربية والأعلام + دعم بروكسي Oxylabs
# =====================================================================

import sys
import subprocess
import os
import time
import threading
import json
import re
from datetime import datetime

# --- 1. التثبيت التلقائي للمكتبات ---
def install_and_import(package, import_name=None):
    if import_name is None:
        import_name = package
    try:
        __import__(import_name)
    except ImportError:
        print(f"📦 جاري تثبيت مكتبة '{package}' تلقائياً...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_and_import("requests")
install_and_import("colorama")
install_and_import("flask")

import requests
from flask import Flask, jsonify, render_template_string, request
from colorama import Fore, Style, init

init(autoreset=True)

# --- 2. قاموس الدول والأعلام العربية الشامل ---
COUNTRY_MAP = {
    "SA": "السعودية 🇸🇦 (SA)",
    "KSA": "السعودية 🇸🇦 (SA)",
    "966": "السعودية 🇸🇦 (SA)",
    "US": "الولايات المتحدة 🇺🇸 (US)",
    "USA": "الولايات المتحدة 🇺🇸 (US)",
    "1": "الولايات المتحدة / كندا 🇺🇸🇨🇦",
    "EG": "مصر 🇪🇬 (EG)",
    "AE": "الإمارات 🇦🇪 (AE)",
    "KW": "الكويت 🇰🇼 (KW)",
    "IQ": "العراق 🇮🇶 (IQ)",
    "JO": "الأردن 🇯🇴 (JO)",
    "MA": "المغرب 🇲🇦 (MA)",
    "QA": "قطر 🇶🇦 (QA)",
    "BH": "البحرين 🇧🇭 (BH)",
    "OM": "عُمان 🇴🇲 (OM)",
    "DZ": "الجزائر 🇩🇿 (DZ)",
    "TN": "تونس 🇹🇳 (TN)",
    "LY": "ليبيا 🇱🇾 (LY)",
    "SD": "السودان 🇸🇩 (SD)",
    "YE": "اليمن 🇾🇪 (YE)",
    "SY": "سوريا 🇸🇾 (SY)",
    "LB": "لبنان 🇱🇧 (LB)",
    "TR": "تركيا 🇹🇷 (TR)",
    "GB": "المملكة المتحدة 🇬🇧 (GB)",
    "UK": "المملكة المتحدة 🇬🇧 (GB)",
    "CA": "كندا 🇨🇦 (CA)",
    "DE": "ألمانيا 🇩🇪 (DE)",
    "FR": "فرنسا 🇫🇷 (FR)",
    "IT": "إيطاليا 🇮🇹 (IT)",
    "ES": "إسبانيا 🇪🇸 (ES)",
    "RU": "روسيا 🇷🇺 (RU)",
    "IN": "الهند 🇮🇳 (IN)",
    "BR": "البرازيل 🇧🇷 (BR)",
    "ID": "إندونيسيا 🇮🇩 (ID)",
    "MY": "ماليزيا 🇲🇾 (MY)",
    "PK": "باكستان 🇵🇰 (PK)"
}

def get_formatted_region(*raw_values):
    """استخراج وتنسيق اسم الدولة الحقيقي مع العلم والتأكد من عدم التخمين الخاطئ"""
    for val in raw_values:
        if val is not None:
            s = str(val).strip().upper()
            if s and s not in ["NONE", "NULL", "UNDEFINED", ""]:
                if s in COUNTRY_MAP:
                    return COUNTRY_MAP[s]
                return f"{s} 🌐"
    return "غير محدد ❓"

# --- 3. الإعدادات والبيانات المعتمدة ---
PROXY_URL = "http://user-iwahm_5Kddd-country-US:pX_sp7ZhSs4hlyJ@dc.oxylabs.io:8000"
SESSION_ID = "78534469621c1064eae0e17393022dee"

PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}

ENDPOINTS = [
    "https://api16-normal-c-useast1a.tiktokv.com/passport/web/account/info/?aid=1233",
    "https://www.tiktok.com/passport/web/account/info/?aid=1459"
]

session_state = {
    "status": "INITIALIZING",
    "last_checked": None,
    "total_pings": 0,
    "successful_pings": 0,
    "failed_pings": 0,
    "error_message": None,
    "account": None,
    "proxy_ip": "جاري الفحص...",
    "proxy_location": "---",
    "proxy_isp": "---"
}

activity_logs = []

def add_log(log_type, message):
    now_str = datetime.now().strftime("%H:%M:%S")
    activity_logs.insert(0, {"id": time.time(), "time": now_str, "type": log_type, "message": str(message)})
    if len(activity_logs) > 35:
        activity_logs.pop()

# ترويسة الجلسة الخاصة لتثبيت موقعك الأمريكى
def get_session_headers():
    clean_sid = SESSION_ID.strip() if SESSION_ID else ""
    return {
        "User-Agent": "TikTok 30.0.0 rv:300013 (iPhone; iOS 16.5; ar_SA) Cronet",
        "Accept": "application/json, text/html, */*",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8",
        "Cookie": f"sessionid={clean_sid}; sessionid_ss={clean_sid}; sid_tt={clean_sid}; store-country-code=us;"
    }

# ترويسة محايدة ونظيفة للبحث عن المستخدمين بدون فرض الكوكي الأمريكي
def get_clean_lookup_headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        "Accept": "application/json, text/html, */*",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8"
    }

# --- 4. فحص اتصال البروكسي ---
def check_proxy_ip():
    try:
        response = requests.get("http://ip-api.com/json/", proxies=PROXIES, timeout=10)
        data = response.json()
        if data.get("status") == "success":
            session_state["proxy_ip"] = str(data.get("query", "---"))
            session_state["proxy_location"] = f"{data.get('country', 'US')} ({data.get('countryCode', 'US')})"
            session_state["proxy_isp"] = str(data.get("isp", "---"))
            add_log("success", f"🌐 IP البروكسي: {session_state['proxy_ip']} [{data.get('country')}]")
            return True
    except Exception as e:
        session_state["proxy_ip"] = "خطأ بالبروكسي"
        add_log("error", f"⚠️ تعذر الاتصال بالبروكسي: {e}")
    return False

# --- 5. نبضة تثبيت الجلسة الخاصة كل 10 ثوانٍ ---
def send_tiktok_ping():
    session_state["total_pings"] += 1
    session_state["last_checked"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    check_proxy_ip()

    add_log("ping", f"⚡ نبضة تثبيت الجلسة رقم (#{session_state['total_pings']}) عبر بروكسي Oxylabs...")

    headers = get_session_headers()
    success = False

    for idx, url in enumerate(ENDPOINTS, 1):
        try:
            res = requests.get(url, headers=headers, proxies=PROXIES, timeout=12)
            res_json = res.json()

            if res_json.get("data") and (res_json["data"].get("user_id") or res_json["data"].get("username")):
                u = res_json["data"]
                session_state["status"] = "LOGGED_IN"
                session_state["successful_pings"] += 1
                session_state["error_message"] = None

                created_date = "غير معلن"
                if u.get("create_time"):
                    try:
                        created_date = datetime.fromtimestamp(int(u.get("create_time"))).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        created_date = str(u.get("create_time"))

                reg_display = get_formatted_region(u.get("country_code"), u.get("region"))

                session_state["account"] = {
                    "user_id": str(u.get("user_id", "---")),
                    "username": str(u.get("username") or u.get("screen_name") or "---"),
                    "nickname": str(u.get("screen_name") or u.get("username") or "---"),
                    "avatar": str(u.get("avatar_url") or ""),
                    "email": str(u.get("email") or "غير معلن"),
                    "mobile": str(u.get("mobile") or "غير معلن"),
                    "created_at": created_date,
                    "region": reg_display
                }

                add_log("success", f"🎉 نجاح الجلسة للمستخدم: @{session_state['account']['username']} | المنطقة: {session_state['account']['region']}")
                success = True
                break
        except Exception as e:
            add_log("error", f"⚠️ تعذر المسار ({idx}): {e}")

    if not success:
        session_state["status"] = "REJECTED"
        session_state["failed_pings"] += 1
        session_state["error_message"] = "Login Expired"
        add_log("error", "❌ تم رفض الجلسة (Login Expired).")

    return success

# نبضة أولية
try:
    send_tiktok_ping()
except Exception as err:
    print("Initial ping error:", err)

# --- 6. حلقة خلفية للنبضات المتواصلة كل 10 ثوانٍ ---
def background_ping_loop():
    print(Fore.GREEN + "🔥 تشغيل خيط الخلفية لنبضات الجلسة كل 10 ثوانٍ...")
    while True:
        try:
            send_tiktok_ping()
        except Exception as err:
            print(f"Background Loop Error: {err}")
        time.sleep(10)

bg_thread = threading.Thread(target=background_ping_loop, daemon=True)
bg_thread.start()

# --- 7. خوارزمية جلب وتحديد الدولة الحقيقية للحسابات العامة ---
def fetch_user_details(username):
    headers = get_clean_lookup_headers()

    # الطريقة الأولى: Web API التفصيلي
    try:
        url = f"https://www.tiktok.com/api/user/detail/?aid=1988&uniqueId={username}"
        res = requests.get(url, headers=headers, proxies=PROXIES, timeout=10).json()
        if res.get("userInfo") and res["userInfo"].get("user"):
            u = res["userInfo"]["user"]
            st = res["userInfo"].get("stats", {})

            region_fmt = get_formatted_region(u.get("region"), u.get("account_region"), u.get("country_code"))

            return {
                "username": u.get("uniqueId") or username,
                "nickname": u.get("nickname") or username,
                "user_id": str(u.get("id") or u.get("uid") or "---"),
                "region": region_fmt,
                "language": str(u.get("language") or "ar").upper(),
                "verified": bool(u.get("verified")),
                "private": bool(u.get("privateAccount")),
                "followers": st.get("followerCount", 0),
                "hearts": st.get("heartCount", 0),
                "following": st.get("followingCount", 0),
                "videos": st.get("videoCount", 0),
                "bio": u.get("signature") or "",
                "avatar": u.get("avatarLarger") or u.get("avatarMedium") or ""
            }
    except Exception as e:
        print("Lookup Method 1 failed:", e)

    # الطريقة الثانية: Mobile Profile API
    try:
        mobile_headers = {
            "User-Agent": "TikTok 30.0.0 rv:300013 (iPhone; iOS 16.5; ar_SA) Cronet",
            "Accept": "application/json"
        }
        url = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/user/profile/other/?unique_id={username}&aid=1233"
        res = requests.get(url, headers=mobile_headers, proxies=PROXIES, timeout=10).json()
        if res.get("user"):
            u = res["user"]
            avatar_url = ""
            if u.get("avatar_larger", {}).get("url_list"):
                avatar_url = u["avatar_larger"]["url_list"][0]
            elif u.get("avatar_thumb", {}).get("url_list"):
                avatar_url = u["avatar_thumb"]["url_list"][0]

            region_fmt = get_formatted_region(u.get("region"), u.get("account_region"), u.get("ip_location"), u.get("country_code"))

            return {
                "username": u.get("unique_id") or username,
                "nickname": u.get("nickname") or username,
                "user_id": str(u.get("uid") or u.get("id") or "---"),
                "region": region_fmt,
                "language": str(u.get("language") or "AR").upper(),
                "verified": bool(u.get("custom_verify") or u.get("enterprise_verify_reason")),
                "private": bool(u.get("secret")),
                "followers": u.get("follower_count", 0),
                "hearts": u.get("total_favorited", 0),
                "following": u.get("following_count", 0),
                "videos": u.get("aweme_count", 0),
                "bio": u.get("signature") or "",
                "avatar": avatar_url
            }
    except Exception as e:
        print("Lookup Method 2 failed:", e)

    # الطريقة الثالثة: تحليل صفحة البروفايل (HTML Rehydration Data)
    try:
        url = f"https://www.tiktok.com/@{username}"
        html_res = requests.get(url, headers=headers, proxies=PROXIES, timeout=10).text
        match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', html_res)
        if match:
            data = json.loads(match.group(1))
            user_scope = data.get("__DEFAULT_SCOPE__", {}).get("webapp.user-detail", {})
            if user_scope.get("userInfo"):
                u = user_scope["userInfo"]["user"]
                st = user_scope["userInfo"].get("stats", {})

                region_fmt = get_formatted_region(u.get("region"), u.get("account_region"), u.get("location"))

                return {
                    "username": u.get("uniqueId") or username,
                    "nickname": u.get("nickname") or username,
                    "user_id": str(u.get("id") or u.get("uid") or "---"),
                    "region": region_fmt,
                    "language": str(u.get("language") or "ar").upper(),
                    "verified": bool(u.get("verified")),
                    "private": bool(u.get("privateAccount")),
                    "followers": st.get("followerCount", 0),
                    "hearts": st.get("heartCount", 0),
                    "following": st.get("followingCount", 0),
                    "videos": st.get("videoCount", 0),
                    "bio": u.get("signature") or "",
                    "avatar": u.get("avatarLarger") or u.get("avatarMedium") or ""
                }
    except Exception as e:
        print("Lookup Method 3 failed:", e)

    return None

# --- 8. واجهة التطبيق الويب (Flask App) ---
app = Flask(__name__)

HTML_UI = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تثبيت الجلسة وباحث تيك توك الشامل 🇺🇸</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
    <style>
        body { font-family: 'Tajawal', sans-serif; }
        .mono { font-family: 'JetBrains Mono', monospace; }
        .console-scrollbar::-webkit-scrollbar { width: 5px; }
        .console-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-4 md:p-8 space-y-6">

    <div class="max-w-4xl mx-auto space-y-6">

        <!-- Header Bar -->
        <div class="flex flex-col md:flex-row justify-between items-center bg-slate-900 border border-slate-800 p-5 rounded-3xl shadow-xl gap-4">
            <div class="flex items-center space-x-3 space-x-reverse">
                <div class="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 text-2xl">
                    <i class="fa-solid fa-satellite-dish animate-pulse"></i>
                </div>
                <div>
                    <h1 class="text-xl font-black text-slate-100">مراقب الجلسة وباحث تيك توك 🇺🇸</h1>
                    <p class="text-xs text-slate-400 font-medium">تثبيت تلقائي كل 10 ثوانٍ عبر Oxylabs Proxy</p>
                </div>
            </div>

            <div id="statusBadge" class="inline-flex items-center space-x-2 space-x-reverse px-4 py-2 rounded-2xl text-xs font-bold bg-slate-800 text-slate-400 border border-slate-700">
                <span class="w-2.5 h-2.5 rounded-full bg-slate-500 animate-pulse"></span>
                <span>جاري الاتصال...</span>
            </div>
        </div>

        <!-- 🔍 كشف واستعلام عن أي حساب -->
        <div class="bg-gradient-to-br from-slate-900 via-slate-900 to-amber-950/30 border border-amber-500/30 rounded-3xl p-6 shadow-2xl space-y-5">
            <div class="flex items-center space-x-3 space-x-reverse border-b border-slate-800 pb-3">
                <i class="fa-solid fa-magnifying-glass text-amber-400 text-lg"></i>
                <h2 class="text-sm font-black text-amber-300 uppercase tracking-wider">كشف واستعلام عن بيانات ودولة أي يوزر تيك توك</h2>
            </div>

            <form onsubmit="searchUser(event)" class="flex flex-col sm:flex-row gap-3">
                <div class="relative flex-1">
                    <span class="absolute inset-y-0 right-0 flex items-center pr-4 text-slate-400 text-sm font-bold">@</span>
                    <input type="text" id="targetUsername" required placeholder="أدخل اسم مستخدم أي شخص (مثال: ksa أو iwahm)" 
                           class="w-full bg-slate-950 border border-slate-800 rounded-2xl pr-9 pl-4 py-3 text-xs text-slate-100 mono outline-none focus:border-amber-500 transition">
                </div>
                <button type="submit" id="searchBtn" class="bg-amber-500 hover:bg-amber-400 text-slate-950 font-black px-6 py-3 rounded-2xl text-xs transition flex items-center justify-center space-x-2 space-x-reverse shadow-lg shadow-amber-500/20">
                    <i id="searchIcon" class="fa-solid fa-search"></i>
                    <span>جلب بيانات الحساب</span>
                </button>
            </form>

            <div id="searchLoading" class="hidden py-8 text-center text-slate-400 text-xs font-medium">
                <i class="fa-solid fa-spinner animate-spin text-2xl mb-2 block text-amber-400"></i>
                جاري جلب دولة الحساب الحقيقية والبيانات...
            </div>

            <div id="searchResultCard" class="hidden bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-4">
                <div class="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-slate-800 pb-4">
                    <div class="flex items-center space-x-4 space-x-reverse">
                        <img id="resAvatar" src="" class="w-16 h-16 rounded-full object-cover border-2 border-amber-500 p-0.5 shadow-md">
                        <div>
                            <div class="flex items-center space-x-2 space-x-reverse">
                                <h3 id="resNickname" class="text-base font-black text-slate-100">---</h3>
                                <span id="resVerified" class="hidden text-blue-400"><i class="fa-solid fa-circle-check"></i></span>
                                <span id="resPrivate" class="hidden bg-slate-800 text-slate-400 px-2 py-0.5 rounded-md text-[10px] font-bold">خاص 🔒</span>
                            </div>
                            <p id="resUsername" class="text-xs text-slate-400 font-medium mono">@---</p>
                        </div>
                    </div>
                    <a id="resProfileLink" href="#" target="_blank" class="bg-slate-900 border border-slate-700 hover:bg-slate-800 text-slate-200 px-4 py-2 rounded-xl text-xs font-bold transition flex items-center space-x-2 space-x-reverse">
                        <i class="fa-solid fa-arrow-up-right-from-square"></i>
                        <span>فتح الحساب في تيك توك</span>
                    </a>
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                    <div class="bg-slate-900 border border-slate-800/80 p-3 rounded-xl">
                        <span class="text-slate-500 text-[10px] block font-bold uppercase">المنطقة / الدولة الحقيقية</span>
                        <span id="resRegion" class="font-black text-amber-400 text-sm">---</span>
                    </div>
                    <div class="bg-slate-900 border border-slate-800/80 p-3 rounded-xl">
                        <span class="text-slate-500 text-[10px] block font-bold uppercase">USER ID</span>
                        <span id="resUserId" class="mono font-bold text-slate-200 text-xs">---</span>
                    </div>
                    <div class="bg-slate-900 border border-slate-800/80 p-3 rounded-xl">
                        <span class="text-slate-500 text-[10px] block font-bold uppercase">عدد المتابعين</span>
                        <span id="resFollowers" class="mono font-bold text-slate-100 text-sm">0</span>
                    </div>
                    <div class="bg-slate-900 border border-slate-800/80 p-3 rounded-xl">
                        <span class="text-slate-500 text-[10px] block font-bold uppercase">إجمالي الإعجابات</span>
                        <span id="resHearts" class="mono font-bold text-slate-100 text-sm">0</span>
                    </div>
                </div>

                <div class="bg-slate-900 border border-slate-800/80 p-3 rounded-xl text-xs space-y-1">
                    <span class="text-slate-500 text-[10px] block font-bold uppercase">السيرة الذاتية (Bio)</span>
                    <p id="resBio" class="text-slate-300 font-medium">---</p>
                </div>
            </div>
        </div>

        <!-- 📌 حالة اتصال الحساب الشخصي -->
        <div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-md space-y-4">
            <h2 class="text-xs font-extrabold text-slate-400 tracking-wider uppercase border-b border-slate-800 pb-3 flex justify-between items-center">
                <span>حالة تثبيت الجلسة الخاصة بك (24/7 Engine)</span>
                <span id="maskedSession" class="mono text-[10px] text-slate-500 font-normal">Session: ---</span>
            </h2>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div class="bg-slate-950 border border-slate-800 p-3 rounded-xl">
                    <span class="text-slate-500 text-[10px] block font-bold">IP البروكسي النشط</span>
                    <span id="activeIp" class="mono font-bold text-amber-400">جاري الفحص...</span>
                </div>
                <div class="bg-slate-950 border border-slate-800 p-3 rounded-xl">
                    <span class="text-slate-500 text-[10px] block font-bold">الموقع المعتمد</span>
                    <span id="ipLocation" class="font-bold text-slate-200">---</span>
                </div>
                <div class="bg-slate-950 border border-slate-800 p-3 rounded-xl">
                    <span class="text-slate-500 text-[10px] block font-bold">عدد النبضات المرسلة</span>
                    <span id="srvPings" class="mono font-bold text-emerald-400">0</span>
                </div>
            </div>

            <!-- Profile Info -->
            <div id="accountDetails" class="hidden bg-slate-950 border border-slate-800/80 rounded-2xl p-4 space-y-3">
                <div class="flex items-center space-x-3 space-x-reverse">
                    <img id="accAvatar" src="" class="w-12 h-12 rounded-full border border-amber-500">
                    <div>
                        <h4 id="accNickname" class="text-sm font-bold text-slate-100">---</h4>
                        <p id="accUsername" class="text-xs text-slate-400 mono">@---</p>
                    </div>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                    <div><span class="text-slate-500">USER ID:</span> <span id="accId" class="mono text-slate-200">---</span></div>
                    <div><span class="text-slate-500">دولة الحساب:</span> <span id="accReg" class="font-bold text-amber-400">---</span></div>
                    <div><span class="text-slate-500">الإيميل:</span> <span id="accEmail" class="mono text-amber-400">---</span></div>
                    <div><span class="text-slate-500">الهاتف:</span> <span id="accPhone" class="mono text-amber-400">---</span></div>
                </div>
            </div>
        </div>

        <!-- 📜 سجل العمليات المباشرة -->
        <div class="bg-slate-900 border border-slate-800 rounded-3xl p-5">
            <h3 class="text-xs font-extrabold text-slate-400 tracking-wider uppercase mb-3 flex justify-between items-center">
                <span>سجل النبضات المتواصلة (كل 10 ثوانٍ)</span>
                <span class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
            </h3>

            <div id="logsConsole" class="bg-slate-950 border border-slate-800/80 rounded-2xl p-4 h-40 overflow-y-auto console-scrollbar space-y-2 mono text-[11px]">
                <div class="text-slate-600">جاري تحميل السجلات...</div>
            </div>
        </div>

    </div>

    <!-- Script -->
    <script>
        async function fetchStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();

                if (data.success) {
                    const state = data.state;
                    const logs = data.logs || [];

                    document.getElementById('activeIp').innerText = state.proxy_ip || 'جاري الفحص...';
                    document.getElementById('ipLocation').innerText = `${state.proxy_location} - ${state.proxy_isp}`;
                    document.getElementById('srvPings').innerText = state.total_pings;
                    document.getElementById('maskedSession').innerText = `Session: ${data.session_masked}`;

                    const badge = document.getElementById('statusBadge');
                    if (state.status === 'LOGGED_IN') {
                        badge.className = 'inline-flex items-center space-x-2 space-x-reverse px-4 py-2 rounded-2xl text-xs font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-800';
                        badge.innerHTML = '<span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span><span>نشط ومسجل الجلسة كل 10 ثوانٍ 🇺🇸</span>';
                    } else if (state.status === 'REJECTED') {
                        badge.className = 'inline-flex items-center space-x-2 space-x-reverse px-4 py-2 rounded-2xl text-xs font-bold bg-rose-950/80 text-rose-300 border border-rose-800';
                        badge.innerHTML = '<span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span><span>الجلسة مرفوضة ❌</span>';
                    }

                    if (state.status === 'LOGGED_IN' && state.account) {
                        const acc = state.account;
                        document.getElementById('accNickname').innerText = acc.nickname;
                        document.getElementById('accUsername').innerText = `@${acc.username}`;
                        document.getElementById('accAvatar').src = acc.avatar;
                        document.getElementById('accId').innerText = acc.user_id;
                        document.getElementById('accReg').innerText = acc.region;
                        document.getElementById('accEmail').innerText = acc.email || 'غير معلن';
                        document.getElementById('accPhone').innerText = acc.mobile || 'غير معلن';
                        document.getElementById('accountDetails').classList.remove('hidden');
                    }

                    const consoleEl = document.getElementById('logsConsole');
                    if (logs.length > 0) {
                        consoleEl.innerHTML = logs.map(l => {
                            let color = 'text-slate-300';
                            if (l.type === 'success') color = 'text-emerald-400 font-bold';
                            if (l.type === 'error') color = 'text-rose-400 font-bold';
                            if (l.type === 'ping') color = 'text-amber-400';
                            return `<div class="py-0.5 border-b border-slate-900/50"><span class="text-slate-500">[${l.time}]</span> <span class="${color}">${l.message}</span></div>`;
                        }).join('');
                    }
                }
            } catch (e) {
                console.error(e);
            }
        }

        async function searchUser(e) {
            e.preventDefault();
            const username = document.getElementById('targetUsername').value.trim();
            if (!username) return;

            const icon = document.getElementById('searchIcon');
            const loading = document.getElementById('searchLoading');
            const resultCard = document.getElementById('searchResultCard');

            icon.className = 'fa-solid fa-spinner fa-spin';
            loading.classList.remove('hidden');
            resultCard.classList.add('hidden');

            try {
                const res = await fetch(`/api/lookup?username=${encodeURIComponent(username)}`);
                const data = await res.json();

                if (data.success) {
                    const u = data.user;
                    document.getElementById('resNickname').innerText = u.nickname;
                    document.getElementById('resUsername').innerText = `@${u.username}`;
                    document.getElementById('resAvatar').src = u.avatar;
                    document.getElementById('resUserId').innerText = u.user_id;
                    document.getElementById('resRegion').innerText = u.region;
                    document.getElementById('resFollowers').innerText = Number(u.followers).toLocaleString();
                    document.getElementById('resHearts').innerText = Number(u.hearts).toLocaleString();
                    document.getElementById('resBio').innerText = u.bio || 'بدون سيرة ذاتية';
                    document.getElementById('resProfileLink').href = `https://www.tiktok.com/@${u.username}`;

                    if (u.verified) document.getElementById('resVerified').classList.remove('hidden');
                    else document.getElementById('resVerified').classList.add('hidden');

                    if (u.private) document.getElementById('resPrivate').classList.remove('hidden');
                    else document.getElementById('resPrivate').classList.add('hidden');

                    resultCard.classList.remove('hidden');
                } else {
                    alert(`تعذر جلب بيانات الحساب: ${data.message}`);
                }
            } catch (err) {
                alert('حدث خطأ أثناء الاتصال بالسيرفر.');
            } finally {
                icon.className = 'fa-solid fa-search';
                loading.classList.add('hidden');
            }
        }

        setInterval(fetchStatus, 3000);
        window.addEventListener('DOMContentLoaded', fetchStatus);
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_UI)

@app.route("/api/status")
def get_status():
    masked_sid = f"{SESSION_ID[:8]}...{SESSION_ID[-4:]}" if SESSION_ID else "غير محدد"
    return jsonify({
        "success": True,
        "session_masked": masked_sid,
        "state": session_state,
        "logs": activity_logs
    })

@app.route("/api/lookup")
def lookup_user():
    username = request.args.get("username", "").strip().replace("@", "")
    if not username:
        return jsonify({"success": False, "message": "اسم المستخدم مطلوب"}), 400

    add_log("ping", f"🔍 جاري كشف بيانات ودولة @{username}...")

    user_data = fetch_user_details(username)
    if user_data:
        add_log("success", f"✅ تم جلب بيانات @{username} | الدولة: {user_data['region']}")
        return jsonify({"success": True, "user": user_data})
    else:
        add_log("error", f"❌ تعذر البحث عن @{username}")
        return jsonify({"success": False, "message": "تعذر البحث عن الحساب أو أنه غير موجود"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


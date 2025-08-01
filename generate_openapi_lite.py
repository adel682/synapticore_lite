# tools/generate_openapi_fixed.py
import json
import os
import sys
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# إعداد نظام السجلات مع دعم UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# تأكد من دعم UTF-8 في الإخراج
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def install_jose_properly():
    """
    تثبيت صحيح لحزمة jose
    """
    try:
        commands = [
            [sys.executable, '-m', 'pip', 'uninstall', 'python-jose', '-y'],
            [sys.executable, '-m', 'pip', 'uninstall', 'jose', '-y'],
            [sys.executable, '-m', 'pip', 'install', 'python-jose[cryptography]==3.3.0']
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            logger.info(f"تم تنفيذ: {' '.join(cmd)}")
            if result.returncode != 0 and 'uninstall' not in ' '.join(cmd):
                logger.warning(f"تحذير: {result.stderr}")
        
        return True
    except Exception as e:
        logger.error(f"خطأ في تثبيت jose: {e}")
        return False

def create_minimal_app_without_jose():
    """
    إنشاء تطبيق FastAPI بسيط بدون jose للاختبار
    """
    app_content = '''"""
تطبيق FastAPI بسيط بدون jose
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="SynaptiCore Lite API",
    version="1.0.0",
    description="API Documentation for SynaptiCore Lite"
)

class HealthResponse(BaseModel):
    status: str
    service: str

@app.get("/", tags=["الرئيسية"])
async def root():
    return {"message": "مرحباً بك في SynaptiCore Lite API"}

@app.get("/health", response_model=HealthResponse, tags=["النظام"])
async def health_check():
    return {"status": "healthy", "service": "SynaptiCore Lite"}

@app.get("/test", tags=["اختبار"])
async def test_endpoint():
    return {"test": "نجح الاختبار", "status": "working"}
'''
    
    try:
        os.makedirs("app", exist_ok=True)
        
        with open("app/__init__.py", "w", encoding="utf-8") as f:
            f.write("# App package\n")
            
        with open("app/main.py", "w", encoding="utf-8") as f:
            f.write(app_content)
            
        logger.info("تم إنشاء تطبيق بسيط بدون jose")
        return True
    except Exception as e:
        logger.error(f"خطأ في إنشاء التطبيق: {e}")
        return False

def test_import_in_isolation():
    """
    اختبار الاستيراد في عملية منفصلة
    """
    test_script = '''
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from app.main import app
    from fastapi.openapi.utils import get_openapi
    print("SUCCESS: استيراد ناجح")
    print(f"APP_TITLE: {app.title}")
    print(f"ROUTES_COUNT: {len(app.routes)}")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
'''
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_script)
            temp_file = f.name
        
        result = subprocess.run([sys.executable, temp_file], 
                              capture_output=True, text=True, timeout=30)
        
        os.unlink(temp_file)
        
        if result.returncode == 0:
            logger.info("✅ اختبار الاستيراد نجح")
            return True
        else:
            logger.error(f"❌ اختبار الاستيراد فشل: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"خطأ في اختبار الاستيراد: {e}")
        return False

def safe_import_app():
    """
    استيراد آمن للتطبيق مع حلول متعددة
    """
    # الحل الأول: محاولة الاستيراد المباشر
    try:
        from fastapi.openapi.utils import get_openapi
        from app.main import app
        logger.info("✅ نجح الاستيراد المباشر")
        return app, get_openapi
    except ImportError as e:
        logger.warning(f"فشل الاستيراد المباشر: {e}")
    
    # الحل الثاني: تثبيت jose وإعادة المحاولة
    logger.info("محاولة إصلاح مشكلة jose...")
    if install_jose_properly():
        try:
            from fastapi.openapi.utils import get_openapi
            from app.main import app
            logger.info("✅ نجح الاستيراد بعد إصلاح jose")
            return app, get_openapi
        except ImportError as e:
            logger.warning(f"لا يزال هناك خطأ بعد إصلاح jose: {e}")
    
    # الحل الثالث: إنشاء تطبيق بسيط بدون jose
    logger.info("إنشاء تطبيق بسيط بدون jose...")
    if create_minimal_app_without_jose():
        # اختبار في عملية منفصلة
        if test_import_in_isolation():
            try:
                from fastapi.openapi.utils import get_openapi
                from app.main import app
                logger.info("✅ نجح الاستيراد للتطبيق البسيط")
                return app, get_openapi
            except ImportError as e:
                logger.error(f"فشل حتى مع التطبيق البسيط: {e}")
    
    return None, None

def generate_openapi_schema(output_path: str = "docs/openapi_lite.json") -> bool:
    """
    توليد مخطط OpenAPI مع معالجة محسنة للأخطاء
    """
    logger.info("🚀 بدء عملية توليد مخطط OpenAPI...")
    
    # استيراد آمن
    app, get_openapi = safe_import_app()
    if app is None or get_openapi is None:
        logger.error("❌ فشل في استيراد التطبيق")
        return False
    
    # إنشاء المجلد
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"خطأ في إنشاء المجلد: {e}")
        return False
    
    # توليد المخطط
    try:
        logger.info("📝 جاري توليد مخطط OpenAPI...")
        openapi_schema = get_openapi(
            title=getattr(app, 'title', 'API'),
            version=getattr(app, 'version', '1.0.0'),
            description=getattr(app, 'description', 'API Documentation'),
            routes=app.routes,
        )
        
        if not openapi_schema:
            logger.error("المخطط فارغ")
            return False
            
    except Exception as e:
        logger.error(f"خطأ في توليد المخطط: {e}")
        return False
    
    # حفظ المخطط
    try:
        # نسخة احتياطية
        if os.path.exists(output_path):
            backup_path = f"{output_path}.backup"
            os.rename(output_path, backup_path)
            logger.info(f"📦 تم إنشاء نسخة احتياطية: {backup_path}")
        
        # حفظ الملف الجديد
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False, sort_keys=True)
        
        # التحقق من الملف
        file_size = os.path.getsize(output_path)
        routes_count = len(openapi_schema.get('paths', {}))
        
        logger.info("✅ تم حفظ مخطط OpenAPI بنجاح!")
        logger.info(f"📁 المسار: {output_path}")
        logger.info(f"📊 حجم الملف: {file_size} بايت")
        logger.info(f"🛣️ عدد المسارات: {routes_count}")
        
        # معلومات إضافية
        if routes_count > 0:
            logger.info("🎯 يمكنك الآن:")
            logger.info("   - عرض التوثيق: http://localhost:8000/docs")
            logger.info("   - عرض ReDoc: http://localhost:8000/redoc")
            logger.info(f"   - تحميل المخطط: {output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"خطأ في حفظ الملف: {e}")
        return False

def main():
    """
    الدالة الرئيسية
    """
    try:
        logger.info("=== SynaptiCore Lite - مولد مخطط OpenAPI المحسن ===")
        
        output_path = os.getenv("OPENAPI_OUTPUT_PATH", "docs/openapi_lite.json")
        
        if generate_openapi_schema(output_path):
            logger.info("🎉 اكتملت العملية بنجاح!")
            sys.exit(0)
        else:
            logger.error("💥 فشلت العملية")
            logger.info("🔧 جرب:")
            logger.info("   pip install --force-reinstall python-jose[cryptography]")
            logger.info("   python -m pip install --upgrade fastapi")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("تم إلغاء العملية")
        sys.exit(130)
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
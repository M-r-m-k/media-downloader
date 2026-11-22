import sys
import os

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# استدعاء التطبيق الرئيسي
try:
    from app import main
    if __name__ == '__main__':
        main()
except Exception as e:
    print(f"Error: {e}")

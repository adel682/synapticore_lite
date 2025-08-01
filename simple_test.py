#!/usr/bin/env python3
"""
اختبار بسيط جداً - يعمل بدون pytest
"""

def test_basic():
    """اختبار أساسي"""
    assert 1 + 1 == 2
    print("✅ الاختبار الأساسي نجح")

def test_strings():
    """اختبار النصوص"""
    assert "hello".upper() == "HELLO"
    print("✅ اختبار النصوص نجح")

def test_lists():
    """اختبار القوائم"""
    data = [1, 2, 3]
    assert len(data) == 3
    print("✅ اختبار القوائم نجح")

def run_all_tests():
    """تشغيل جميع الاختبارات"""
    tests = [test_basic, test_strings, test_lists]
    passed = 0
    failed = 0
    
    print("🚀 بدء تشغيل الاختبارات البسيطة")
    print("=" * 40)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} فشل: {e}")
            failed += 1
    
    print("=" * 40)
    print(f"📊 النتائج: {passed} نجح, {failed} فشل")
    
    if failed == 0:
        print("🎉 جميع الاختبارات نجحت!")
        return True
    else:
        print("⚠️  بعض الاختبارات فشلت")
        return False

if __name__ == "__main__":
    run_all_tests()

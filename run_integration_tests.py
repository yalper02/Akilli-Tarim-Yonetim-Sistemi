import sys
import pytest

def main():
    print("=" * 70)
    print("   ATYS ML MIKRO-SERVIS INTEGRASYON VE SLA TEST KOSUCUSU")
    print("=" * 70)
    print("\nPytest entegrasyon testleri baslatiliyor...\n")
    
    # ml_service/test_ml_service.py dosyasındaki testleri calistir
    # -v: verbose, -s: print ifadelerini göster
    retcode = pytest.main(["-v", "-s", "ml_service/test_ml_service.py"])
    
    print("\n" + "=" * 70)
    if retcode == 0:
        print("   TUM ENTEGRASYON VE SLA TESTLERI BASARIYLA GECTI! (exit 0)")
        print("=" * 70)
        sys.exit(0)
    else:
        print("   BAZI ENTEGRASYON TESTLERI BASARISIZ OLDU! (exit 1)")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()

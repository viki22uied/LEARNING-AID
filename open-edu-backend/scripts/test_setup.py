#!/usr/bin/env python3
"""
Test script to verify the Open Educational Resources Recommendation Backend setup
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_config():
    """Test configuration loading"""
    try:
        from app.config import settings
        print("✅ Configuration loaded successfully")
        print(f"   - API Host: {settings.api_host}")
        print(f"   - API Port: {settings.api_port}")
        print(f"   - Database URL: {settings.database_url}")
        print(f"   - Embeddings Model: {settings.embeddings_model}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def test_database():
    """Test database connection"""
    try:
        from app.core.database import init_db, close_db
        await init_db()
        print("✅ Database connection successful")
        await close_db()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def test_embeddings():
    """Test embeddings service"""
    try:
        from app.services.ml.embeddings import embeddings_service
        await embeddings_service.load_model()
        print("✅ Embeddings service loaded successfully")
        print(f"   - Model: {embeddings_service.model_name}")
        print(f"   - Dimension: {embeddings_service.get_dimension()}")
        return True
    except Exception as e:
        print(f"❌ Embeddings test failed: {e}")
        return False

async def test_vector_store():
    """Test vector store"""
    try:
        from app.services.ml.vector_store import vector_store
        await vector_store.initialize(384)
        print("✅ Vector store initialized successfully")
        print(f"   - Type: {vector_store.vector_db_type}")
        return True
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False

async def test_stt():
    """Test STT service"""
    try:
        from app.services.ml.stt import stt_service
        await stt_service.load_model()
        print("✅ STT service loaded successfully")
        print(f"   - Model: {stt_service.model_name}")
        return True
    except Exception as e:
        print(f"❌ STT test failed: {e}")
        return False

async def test_concept_extractor():
    """Test concept extractor"""
    try:
        from app.services.ml.concept_extractor import concept_extractor
        await concept_extractor.initialize()
        print("✅ Concept extractor initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Concept extractor test failed: {e}")
        return False

async def test_search():
    """Test search service"""
    try:
        from app.services.search import search_service
        print("✅ Search service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Search service test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing Open Educational Resources Recommendation Backend Setup")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_config),
        ("Database", test_database),
        ("Embeddings", test_embeddings),
        ("Vector Store", test_vector_store),
        ("STT", test_stt),
        ("Concept Extractor", test_concept_extractor),
        ("Search", test_search),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("\nTo start the application, run:")
        print("   python scripts/start.py")
        print("   or")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

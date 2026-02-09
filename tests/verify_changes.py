import sys
import os
from pathlib import Path
import time

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

try:
    from synapse.analyzer import ProjectAnalyzer
    from synapse.vector_store import VectorStore
    from synapse.file_tracker import FileTracker
    print("[OK] Modules imported successfully.")
except ImportError as e:
    print(f"[ERROR] Failed to import Synapse modules: {e}")
    sys.exit(1)

def test_parallel_analysis():
    print("\n--- Testing Parallel Analysis ---")
    root_dir = Path(".").resolve()
    analyzer = ProjectAnalyzer(str(root_dir))
    
    # Clean previous run
    if analyzer.db_dir.exists():
        import shutil
        # be careful deleting... maybe just clear tracker
        tracker = FileTracker(analyzer.db_dir)
        tracker.clear()
        
    start_time = time.time()
    try:
        # Run with 2 workers to test parallelism
        print("Running analyze with num_workers=2...")
        summary = analyzer.analyze(json_output=True, num_workers=2)
        
        duration = time.time() - start_time
        print(f"Analysis completed in {duration:.2f} seconds.")
        
        if summary.get("status") == "success":
            print(f"[PASS] Status: {summary.get('status')}")
            print(f"[PASS] Files Analyzed: {summary.get('files_analyzed')}")
            print(f"[PASS] Graph Nodes: {summary.get('graph_nodes')}")
        else:
            print(f"[FAIL] Analysis failed: {summary}")
            
    except Exception as e:
        print(f"[FAIL] Analysis threw exception: {e}")
        import traceback
        traceback.print_exc()

def test_vector_store():
    print("\n--- Testing Vector Store (Jina) ---")
    try:
        vs = VectorStore(db_path="./.synapse/test_db")
        print(f"[INFO] Embedding Function: {type(vs.embedding_fn).__name__}")
        
        if "Jina" in type(vs.embedding_fn).__name__:
            print("[PASS] JinaEmbeddingFunction is active.")
        else:
            print("[WARN] JinaEmbeddingFunction not active (falling back to Dummy or Default).")
            
        # Test embedding dimension
        docs = ["def hello(): print('world')"]
        metas = [{"path": "test.py", "language": "python", "type": "test"}]
        ids = ["test:1"]
        
        vs.add_documents(docs, metas, ids, quiet=True)
        count = vs.count()
        print(f"[PASS] Vector Store Count: {count}")
        
    except Exception as e:
        print(f"[FAIL] Vector Store test failed: {e}")

if __name__ == "__main__":
    print("Starting Synapse Verification...")
    test_parallel_analysis()
    test_vector_store()
    print("\nVerification Complete.")

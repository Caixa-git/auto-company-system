#!/usr/bin/env python3
"""
ACS Test Runner — 전체 TC 통합 실행
사용법:
  python3 scripts/run_all_tests.py              # 전체 실행
  python3 scripts/run_all_tests.py --phase 1    # Phase 1만
  python3 scripts/run_all_tests.py --tc 1.1.1   # 특정 TC만
"""
import sys, os, json, subprocess, re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"

TESTS = {
    "1.1.1": {
        "name": "기본 메시지 스키마",
        "runner": "python3 scripts/validate_message.py",
        "phase": 1,
    },
    "1.1.3": {
        "name": "HOTL 위급도 라우팅",
        "runner": "python3 scripts/tc_1_1_3.py",
        "phase": 1,
    },
    "1.1.4": {
        "name": "에스컬레이션 payload 변조 방지",
        "runner": "python3 scripts/tc_1_1_4.py",
        "phase": 1,
    },
    # 1.1.2 완료 후 추가
    # 1.1.3 완료 후 추가
    # 1.2.x 완료 후 추가
}

def print_header(text):
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)

def run_test(tc_id, info):
    print_header(f"TC-{tc_id}: {info['name']}")
    result = subprocess.run(
        info["runner"], shell=True, cwd=ROOT,
        capture_output=True, text=True, timeout=60
    )
    print(result.stdout)
    if result.stderr:
        print(f"  ⚠️ stderr: {result.stderr[:200]}")
    return result.returncode == 0, result.returncode

def load_roadmap_tcs():
    """ROADMAP.md에서 TC 상태 읽기"""
    roadmap = ROOT / "ROADMAP.md"
    if not roadmap.exists():
        return {}
    
    with open(roadmap) as f:
        content = f.read()
    
    tcs = {}
    # TC-1.1.1 같은 패턴 찾기
    for m in re.finditer(r'(TC-[\d.]+)[—\s]+(.*?)(?=\n(?:TC-|\||$))', content):
        tc_id = m.group(1).replace("TC-", "")
        desc = m.group(2).strip()[:60]
        tcs[tc_id] = desc
    
    return tcs

def main():
    phase_filter = None
    tc_filter = None
    
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--phase" and i + 1 < len(args):
            phase_filter = int(args[i + 1])
        elif arg == "--tc" and i + 1 < len(args):
            tc_filter = args[i + 1]
    
    # ROADMAP TC 상태 출력
    roadmap_tcs = load_roadmap_tcs()
    if roadmap_tcs:
        print_header("ROADMAP TC 현황")
        for tc_id, desc in sorted(roadmap_tcs.items()):
            status = "✅" if tc_id in TESTS else "⬜"
            print(f"  {status} TC-{tc_id}: {desc}")
    
    # 필터링
    targets = {}
    for tc_id, info in TESTS.items():
        if tc_filter and tc_id != tc_filter:
            continue
        if phase_filter and info["phase"] != phase_filter:
            continue
        targets[tc_id] = info
    
    if not targets:
        print("\n  실행할 TC 없음 (아직 등록 안 됨)")
        return
    
    # 실행
    passed = 0
    failed = 0
    results = []
    
    for tc_id in sorted(targets.keys(), key=lambda x: [int(p) for p in x.split('.')]):
        info = targets[tc_id]
        ok, rc = run_test(tc_id, info)
        if ok:
            passed += 1
            results.append(f"  ✅ TC-{tc_id}")
        else:
            failed += 1
            results.append(f"  ❌ TC-{tc_id} (rc={rc})")
    
    # 요약
    print_header("최종 결과")
    for r in results:
        print(r)
    print(f"\n  {passed} 통과, {failed} 실패 (총 {passed + failed}개)")
    
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()

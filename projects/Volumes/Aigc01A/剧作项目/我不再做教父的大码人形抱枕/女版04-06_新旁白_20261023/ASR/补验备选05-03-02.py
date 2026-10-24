# -*- coding: utf-8 -*-
"""One explicitly authorized alternative only; never edits the24-input manifest.
Default prepares exact mapping only; --execute independently accepts take02.
No path override, broad scan, browser, Resolve, audio editing or adoption action.
"""
from pathlib import Path
import argparse,datetime as dt,hashlib,importlib.util,json,re,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('female_voice_acceptance',HERE/'验收女版04-06.py')
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--execute',action='store_true');args=ap.parse_args()
 assert q.TASK.name=='女版04-06_新旁白_20261023'
 manifest_bytes=q.MANIFEST.read_bytes();manifest_sha=hashlib.sha256(manifest_bytes).hexdigest();assert manifest_sha==q.MANIFEST_SHA_PIN
 m=json.loads(manifest_bytes);assert len(m['groups'])==24 and m['version']=='女版'
 g=next(g for g in m['groups']if g['episode']==5 and g['narration_sequence']==3 and g['take']==1)
 assert q.digest(g['text_file'])==g['generation_text_sha256']
 assert Path(g['text_file']).read_text(encoding='utf-8')==g['generation_text']
 source=q.TASK/'备选版本/第05集/大码女版枕头05-03-02.mp3'
 assert source.resolve().is_relative_to(q.TASK.resolve())
 row=dict(episode=5,sequence=3,take=2,basename='大码女版枕头05-03-02',source_path=str(source),canonical_text=g['generation_text'],text_sha256=g['generation_text_sha256'],text_path=g['text_file'],docx_paragraphs=g['source_docx_paragraphs'],expected_voice=q.EXPECTED_VOICE,speed_percent=100,alternative_authorization='Root明确授权同正确平台记录现成第2版本，单独只读补验；不重新生成、不覆盖01。',original_primary_basename=g['basename'],original_primary_audio_path=g['planned_audio_path'])
 scope=dict(status='EXPLICIT_SINGLE_ALTERNATIVE_PREPARED_NO_ASR',prepared_at_utc=q.stamp(),source_path=str(source),original_text_manifest=q.MANIFEST.as_posix(),original_manifest_sha256=manifest_sha,manifest_24_input_mapping_unchanged=True,row=row,audio_decoded=False,asr_started=False,not_an_adoption_or_audio_rename=True)
 q.save(HERE/'备选05-03-02_显式授权映射.json',scope)
 if not args.execute:
  print(json.dumps(scope,ensure_ascii=False));return
 runtime=q.configure_runtime();rec,cached=q.process(row,runtime)
 assert q.MANIFEST.read_bytes()==manifest_bytes,'Original24-input manifest must not change'
 def tokens(t):return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+",t.lower().replace('’',"'"))
 def names(t):return [{'mateo':'matteo',"mateo's":"matteo's"}.get(w,w)for w in tokens(t)]
 exact_after_names=names(row['canonical_text'])==names(rec['text'])
 diary_words=[w for w in rec['words']if w['word'].strip(' .,!?;:').lower()in ('diary','diore','diori')]
 result=dict(status='ALTERNATIVE_TEXT_COVERAGE_PASS_PENDING_VOICE_LISTEN'if exact_after_names else'ALTERNATIVE_REVIEW_REQUIRED',checked_at_utc=q.stamp(),row=row,source_sha256=rec['source_sha256'],raw_asr_path=str(HERE/'raw_large-v3-turbo/narration/大码女版枕头05-03-02.json'),raw_asr_text=rec['text'],raw_flags_preserved=rec['quality_flags'],comparison=rec['comparison'],only_name_spelling_normalization_matches_source=exact_after_names,diary_word_candidates=diary_words,cache_reused_without_asr=cached,duration_seconds=rec['pcm_measurements']['decoded_duration_seconds'],source_audio_modified=False,original_take01_cache_modified=False,original_manifest_unchanged=True,production_progress_modified=False,adopted=False,adoption_decision_owned_by_root=True,human_listening_verified=False)
 q.save(HERE/'备选05-03-02_补验.json',result)
 print(json.dumps(result,ensure_ascii=False),flush=True)
if __name__=='__main__':main()

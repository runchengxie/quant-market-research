import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { createHash } from 'node:crypto';
import { parseCsv } from './csv.mjs';
import { valuationCaseCopy } from '../src/content/valuation-case-copy.ts';
import { assertPublicRound2, buildRound2Evidence, validateControlReceiptChain } from '../src/lib/valuation-round2.ts';
const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, item, i, all) => i % 2 ? pairs : [...pairs, [item, all[i + 1]]], []));
for (const key of ['--unresolved-root','--rules','--freeze-receipt','--output','--receipt']) if (!args[key]) throw new Error('Missing ' + key);
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const inputs = {}, hashes = {};
function read(path, key) { const bytes = readFileSync(resolve(path)); inputs[key] = resolve(path); hashes[key] = sha(bytes); return JSON.parse(bytes); }
const root = resolve(args['--unresolved-root']);
const sourceReceipt = read(resolve(root, 'receipt.json'), 'sensitivity_receipt');
if (sourceReceipt.status !== 'completed_readonly_valuation_sensitivity') throw new Error('Unreviewed source status');
function verified(file,key) {
  const data = read(resolve(root,file),key);
  if (hashes[key] !== sourceReceipt.outputs[file]) throw new Error('Source hash mismatch: ' + key);
  return data;
}
const rules = read(args['--rules'],'rules'), freeze = read(args['--freeze-receipt'],'freeze_receipt');
if (!Object.values(freeze.inputs).includes(hashes.sensitivity_receipt) || sourceReceipt.run_receipt_sha256 !== rules.source_run_receipt_sha256) throw new Error('Source is not the frozen run');
let attribution;
if (args['--attribution-root']) {
 const attrRoot=resolve(args['--attribution-root']);
 const receipt=read(resolve(attrRoot,'receipt.json'),'attribution_receipt');
 if (receipt.status!=='completed_readonly_attribution' || receipt.reconciliation_passed!==true || receipt.rules_sha256!==hashes.rules || receipt.run_receipt_sha256!==rules.source_run_receipt_sha256) throw new Error('Attribution receipt differs from frozen rules/run');
 const attrRead=(file,key)=>{const value=read(resolve(attrRoot,file),key);if(hashes[key]!==receipt.outputs[file]) throw new Error('Attribution hash mismatch');return value;};
 const annualBytes=readFileSync(resolve(attrRoot,'annual_attribution.csv'));
 inputs.attribution_annual=resolve(attrRoot,'annual_attribution.csv');hashes.attribution_annual=sha(annualBytes);
 if(hashes.attribution_annual!==receipt.outputs['annual_attribution.csv']) throw new Error('Annual attribution hash mismatch');
 attribution={summary:attrRead('summary.json','attribution_summary'),reconciliation:attrRead('reconciliation.json','attribution_reconciliation'),annual:parseCsv(annualBytes.toString('utf8'))};
}
let controls, controlsSemantics, controlsAudit;
if(args['--controls-root']) {
 if(!attribution) throw new Error('Controls require the bound attribution source');
 const controlRoot=resolve(args['--controls-root']);
 const receipt=read(resolve(controlRoot,'receipt.json'),'controls_receipt');
 controls=read(resolve(controlRoot,'summaries.json'),'controls_summary');
 if(hashes.controls_summary!==receipt.outputs['summaries.json']) throw new Error('Control summary hash mismatch');
 const supplemental=read(resolve(controlRoot,'supplemental_receipt.json'),'controls_supplemental_receipt');
 const semanticsReceipt=read(resolve(controlRoot,'semantics_receipt.json'),'controls_semantics_receipt');
 const crossAudit=read(resolve(controlRoot,'cross_receipt_audit.json'),'controls_cross_receipt_audit');
 if(hashes.controls_cross_receipt_audit!==supplemental.outputs['cross_receipt_audit.json']) throw new Error('Cross-receipt audit hash mismatch');
 validateControlReceiptChain(receipt,supplemental,semanticsReceipt,crossAudit,hashes);
 const bucketPath=resolve(controlRoot,'feature_bucket_balance.csv'),bucketBytes=readFileSync(bucketPath);
 inputs.controls_bucket_balance=bucketPath;hashes.controls_bucket_balance=sha(bucketBytes);
 if(hashes.controls_bucket_balance!==supplemental.outputs['feature_bucket_balance.csv']) throw new Error('Bucket audit hash mismatch');
 controlsSemantics=read(resolve(controlRoot,'summary_semantics.json'),'controls_semantics');
 if(hashes.controls_semantics!==semanticsReceipt.outputs['summary_semantics.json']) throw new Error('Semantic addendum hash mismatch');
 controlsAudit={cross_receipt_passed:true,bucket_distribution_audited:true,bucket_aggregate_rows:supplemental.bucket_rows,semantics_checked:true,recovered_seal:receipt.status==='recovered_after_receipt_only_failure'};
}
let cases,caseAudit;
if(args['--cases-root']) {
 const caseRoot=resolve(args['--cases-root']),receipt=read(resolve(caseRoot,'receipt.json'),'case_receipt');
 if(!args['--case-receipt-sha256'] || hashes.case_receipt!==args['--case-receipt-sha256'] || receipt.status!=='completed_bounded_audit_with_explicit_gaps' ||
    receipt.rules_unchanged!==true || receipt.selection_unchanged!==true || receipt.raw_data_changed!==false || receipt.ledger_recalculated!==false ||
    receipt.recovery_cash_booked!==false || receipt.revision_safe!==false || !Object.values(receipt.inputs).includes(hashes.freeze_receipt) ||
    !Object.values(receipt.inputs).includes(hashes.attribution_receipt) || !Object.values(receipt.inputs).includes(hashes.rules)) throw new Error('Case receipt differs from reviewed frozen chain');
 cases=read(resolve(caseRoot,'public_cases.json'),'case_facts');caseAudit=read(resolve(caseRoot,'audit.json'),'case_audit');
 if(hashes.case_facts!==receipt.outputs['public_cases.json'] || hashes.case_audit!==receipt.outputs['audit.json']) throw new Error('Case output hash mismatch');
 const copyPath=resolve('src/content/valuation-case-copy.ts');
 inputs.case_copy=copyPath;hashes.case_copy=sha(readFileSync(copyPath));
}
const data = buildRound2Evidence({ sensitivities: verified('sensitivities.json','sensitivities'), unresolved: verified('summary.json','unresolved_summary'),
  checkpoint: read('public/data/valuation_ledger_checkpoint_draft.json','checkpoint'), rules, freeze, rulesHash: hashes.rules, sourceHashes: hashes, attribution, controls, controlsSemantics, controlsAudit, cases, caseAudit, caseCopy:valuationCaseCopy });
assertPublicRound2(data);
const output = resolve(args['--output']), receipt = resolve(args['--receipt']);
if (existsSync(receipt)) throw new Error('Refusing to overwrite receipt');
const bytes = Buffer.from(JSON.stringify(data)+'\n');
if (existsSync(output) && !readFileSync(output).equals(bytes)) throw new Error('Refusing to overwrite different public evidence');
mkdirSync(dirname(receipt),{recursive:true});
if (!existsSync(output)) writeFileSync(output,bytes,{flag:'wx'});
writeFileSync(receipt,JSON.stringify({ status:'prepared_unpublished_allowlisted_aggregate',inputs,input_sha256:hashes,output,output_sha256:sha(bytes),
  source_sha256:{ 'web/src/lib/valuation-round2.ts':sha(readFileSync(new URL('../src/lib/valuation-round2.ts',import.meta.url))), 'web/scripts/prepare-valuation-round2.mjs':sha(readFileSync(new URL(import.meta.url))) } },null,2)+'\n',{flag:'wx'});
console.log('Prepared '+data.sensitivities.length+' sensitivity rows with frozen rules');

/**
 * 금강 쓰레기 AI 프로젝트 - 구글 시트 저장용 Apps Script
 *
 * 1) 구글 시트를 새로 만들고  확장 프로그램 > Apps Script 를 엽니다.
 * 2) 이 코드를 모두 붙여 넣고, 아래 TOKEN 값을 원하는 비밀 문자열로 바꿉니다.
 * 3) 배포 > 새 배포 > 유형: 웹 앱
 *      - 실행 사용자: 나
 *      - 액세스 권한: 모든 사용자
 *    배포 후 나오는 웹 앱 URL을 Streamlit secrets의 APPS_SCRIPT_URL에 넣습니다.
 */
const TOKEN = '여기에-비밀문자열을-넣으세요';

function doPost(e) {
  const body = JSON.parse(e.postData.contents);
  if (body.token !== TOKEN) return out_({ ok: false, error: 'token' });

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(body.sheet) || ss.insertSheet(body.sheet);
    const rec = body.record || {};
    let header = sh.getLastRow() > 0
      ? sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0].map(String)
      : [];
    Object.keys(rec).forEach(function (k) { if (header.indexOf(k) < 0) header.push(k); });
    sh.getRange(1, 1, 1, header.length).setValues([header]).setFontWeight('bold');
    sh.appendRow(header.map(function (k) { return rec[k] === undefined ? '' : rec[k]; }));
    return out_({ ok: true });
  } finally {
    lock.releaseLock();
  }
}

function doGet(e) {
  if (e.parameter.token !== TOKEN) return out_({ ok: false, error: 'token' });
  const sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(e.parameter.sheet);
  if (!sh || sh.getLastRow() < 2) return out_({ ok: true, rows: [] });
  const values = sh.getDataRange().getDisplayValues();
  const header = values.shift();
  const rows = values.map(function (r) {
    const o = {};
    header.forEach(function (k, i) { o[k] = r[i]; });
    return o;
  });
  return out_({ ok: true, rows: rows });
}

function out_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

/**
 * Marev Stars Support notification relay.
 *
 * Required Script properties:
 * SUPPORT_RECIPIENT       e.g. marevstars.support@gmail.com
 * SUPPORT_WEBHOOK_SECRET  a long random string, identical to Render's
 *                         GOOGLE_APPS_SCRIPT_SECRET value.
 */
function doPost(e) {
  let data;
  try {
    data = JSON.parse((e && e.postData && e.postData.contents) || '{}');
  } catch (error) {
    return json_({ ok: false, error: 'Invalid JSON request.' });
  }

  const properties = PropertiesService.getScriptProperties();
  const recipient = properties.getProperty('SUPPORT_RECIPIENT');
  const expectedSecret = properties.getProperty('SUPPORT_WEBHOOK_SECRET');

  if (!recipient || !expectedSecret || data.secret !== expectedSecret) {
    return json_({ ok: false, error: 'Unauthorized request.' });
  }
  if (!data.subject || !data.text) {
    return json_({ ok: false, error: 'Missing notification content.' });
  }

  try {
    GmailApp.sendEmail(recipient, data.subject, data.text, {
      name: 'Marev Stars Support',
    });
    return json_({ ok: true });
  } catch (error) {
    console.error(error);
    return json_({ ok: false, error: 'Gmail could not send the notification.' });
  }
}

function json_(value) {
  return ContentService
    .createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}

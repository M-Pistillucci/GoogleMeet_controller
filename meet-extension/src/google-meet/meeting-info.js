/**
 * Estrae le informazioni correnti sulla riunione Google Meet dal DOM e dall'URL.
 */

export function getMeetingId() {
  const path = window.location.pathname;
  const match = path.match(/^\/([a-z]{3}-[a-z]{4}-[a-z]{3})/);
  return match ? match[1] : null;
}

export function getMeetingName() {
  if (!isInMeeting()) return null;
  const title = document.title || '';
  const cleanTitle = title.replace(/^Meet\s*-\s*/i, '').trim();
  return cleanTitle || null;
}

export function getParticipantCount() {
  if (!isInMeeting()) return 0;

  const countElement = document.querySelector('div[data-participant-count]') ||
                       document.querySelector('[aria-label*="partecipanti"], [aria-label*="people"]');

  if (countElement) {
    const countAttr = countElement.getAttribute('data-participant-count');
    if (countAttr) return parseInt(countAttr, 10);

    const textMatch = countElement.textContent.match(/\d+/);
    if (textMatch) return parseInt(textMatch[0], 10);
  }

  return 0;
}

export function isInMeeting() {
  const path = window.location.pathname;
  const isMeetingUrl = /^\/[a-z]{3}-[a-z]{4}-[a-z]{3}$/.test(path);

  const hasControls = document.querySelector('button[data-is-muted]') !== null ||
                      document.querySelector('button[data-key-shortcut]') !== null;

  return isMeetingUrl && hasControls;
}

/**
 * Raggruppa tutte le info di contesto della riunione in un unico oggetto.
 */
export function getMeetingDetails() {
  const inCall = isInMeeting();

  return {
    in_meeting: inCall,
    meeting_id: inCall ? getMeetingId() : null,
    meeting_name: inCall ? getMeetingName() : null,
    participant_count: inCall ? getParticipantCount() : 0
  };
}

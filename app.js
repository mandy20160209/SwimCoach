(() => {
  const store = window.SwimCoachStorage;
  const $ = (id) => document.getElementById(id);
  const saved = store.read();

  document.querySelectorAll('input[name="level"]').forEach((input) => {
    input.checked = input.value === saved.level;
    input.addEventListener('change', () => {
      store.write({ level: input.value });
      $('levelResult').textContent = `Saved: ${input.parentElement.querySelector('b').textContent}. Your next plan will start here.`;
    });
  });

  $('postureDescriptionInput').value = saved.postureDescription || '';
  $('describePosture').addEventListener('click', () => {
    const description = $('postureDescriptionInput').value.trim();
    if (!description) {
      $('postureDescriptionText').textContent = 'Write a few words about what you notice first, and I will help describe it.';
    } else {
      const lower = description.toLowerCase();
      const tips = [];
      if (lower.includes('head') || lower.includes('look') || lower.includes('high')) tips.push('Your description mentions your head or gaze. Try looking toward the pool floor and keeping your neck relaxed.');
      if (lower.includes('hip') || lower.includes('leg') || lower.includes('sink')) tips.push('Your description mentions your hips or legs. Try making your body long and keeping your hips closer to the surface.');
      if (lower.includes('line') || lower.includes('straight') || lower.includes('body')) tips.push('Your description mentions your body line. Try reaching forward and pointing your toes so your body feels long and straight.');
      if (lower.includes('breath') || lower.includes('breathe')) tips.push('For breathing, turn your head with your body instead of lifting it. Practice this with a coach in a safe place.');
      $('postureDescriptionText').textContent = tips.length ? tips.join(' ') : `You described: “${description}” Start by asking a coach to watch this part from the side, then practice one small change at a time.`;
    }
    $('postureDescription').hidden = false;
    store.write({ postureDescription: description });
  });

  $('resetProgress').addEventListener('click', () => { if (confirm('Clear the progress saved on this computer?')) { store.reset(); location.reload(); } });

  $('askButton').addEventListener('click', async () => {
    const question = $('question').value.trim();
    if (!question) { $('askStatus').textContent = 'Type a question first.'; return; }
    if (!$('thoughtFirst').checked) { $('askStatus').textContent = 'Describe what you notice first, then check the box.'; return; }
    const button = $('askButton'); button.disabled = true; $('askStatus').textContent = 'Thinking…'; $('answerBox').hidden = true;
    try {
      const current = store.read();
      const response = await fetch('/api/coach', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question, level: current.level || 'not chosen', postureDescription: current.postureDescription || '' }) });
      const data = await response.json();
      if (!response.ok) {
        const problem = typeof data.error === 'object' ? data.error : { message: data.error };
        if (problem.fix) console.warn('SwimCoach fix:', problem.fix);
        throw new Error(problem.message || 'The coach could not answer.');
      }
      $('answerText').textContent = data.answer; $('answerBox').hidden = false; $('askStatus').textContent = 'Answer ready.'; store.write({ questionsAsked: current.questionsAsked + 1 });
    } catch (error) { $('askStatus').textContent = error.message || 'Please check the key service and internet connection.'; }
    finally { button.disabled = false; }
  });
})();

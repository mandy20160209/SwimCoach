(() => {
  const store = window.SwimCoachStorage;
  const $ = (id) => document.getElementById(id);
  let stream = null;
  const saved = store.read();
  document.querySelectorAll('input[name="level"]').forEach((input) => {
    input.checked = input.value === saved.level;
    input.addEventListener('change', () => {
      store.write({ level: input.value });
      $('levelResult').textContent = `Saved: ${input.parentElement.querySelector('b').textContent}. Your next plan will start here.`;
    });
  });
  document.querySelectorAll('[data-reflection]').forEach((input) => { input.checked = saved.reflections.includes(input.dataset.reflection); });
  $('saveReflection').addEventListener('click', () => {
    const reflections = [...document.querySelectorAll('[data-reflection]:checked')].map((input) => input.dataset.reflection);
    store.write({ reflections });
    $('cameraMessage').textContent = reflections.length ? 'Saved. You noticed something important.' : 'Saved. You can notice more next time.';
  });
  $('describePosture').addEventListener('click', () => {
    const reflections = [...document.querySelectorAll('[data-reflection]:checked')].map((input) => input.dataset.reflection);
    const descriptions = {
      head: 'Your observation suggests your head may be lifted. Try looking down at the pool floor and keeping your neck relaxed.',
      hips: 'Your observation suggests your hips or legs may sink. Try making your body long and keeping your hips closer to the surface.',
      line: 'Your observation suggests your body line may not feel long and straight yet. Try reaching forward and pointing your toes.',
      unsure: 'You are not sure yet, and that is okay. Ask a coach to watch you from the side or use a short posture lesson.'
    };
    const text = reflections.length ? reflections.map((item) => descriptions[item]).join(' ') : 'Choose what you notice first, then I can describe your starting posture in simple words.';
    $('postureDescriptionText').textContent = text;
    $('postureDescription').hidden = false;
    store.write({ reflections });
  });
  $('resetProgress').addEventListener('click', () => { if (confirm('Clear the progress saved on this computer?')) { store.reset(); location.reload(); } });
  $('startCamera').addEventListener('click', async () => {
    if (!navigator.mediaDevices?.getUserMedia) { $('cameraMessage').textContent = 'This browser cannot use the camera here.'; return; }
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
      $('cameraVideo').srcObject = stream; $('cameraVideo').hidden = false; $('cameraPlaceholder').hidden = true; $('cameraGuide').hidden = false; $('startCamera').disabled = true; $('stopCamera').disabled = false; $('cameraMessage').textContent = 'Camera is on. Your video is not sent to the AI.';
    } catch { $('cameraMessage').textContent = 'Camera access was not given. You can still use the posture lessons.'; }
  });
  $('stopCamera').addEventListener('click', stopCamera);
  function stopCamera() { if (stream) stream.getTracks().forEach((track) => track.stop()); stream = null; $('cameraVideo').hidden = true; $('cameraGuide').hidden = true; $('cameraPlaceholder').hidden = false; $('startCamera').disabled = false; $('stopCamera').disabled = true; $('cameraMessage').textContent = 'Camera is off.'; }
  $('askButton').addEventListener('click', async () => {
    const question = $('question').value.trim();
    if (!question) { $('askStatus').textContent = 'Type a question first.'; return; }
    if (!$('thoughtFirst').checked) { $('askStatus').textContent = 'Think about what you notice first, then check the box.'; return; }
    const button = $('askButton'); button.disabled = true; $('askStatus').textContent = 'Thinking…'; $('answerBox').hidden = true;
    try {
      const response = await fetch('/api/coach', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question, level: store.read().level || 'not chosen', reflections: store.read().reflections }) });
      const data = await response.json();
      if (!response.ok) {
        const problem = typeof data.error === 'object' ? data.error : { message: data.error };
        if (problem.fix) console.warn('SwimCoach fix:', problem.fix);
        throw new Error(problem.message || 'The coach could not answer.');
      }
      $('answerText').textContent = data.answer; $('answerBox').hidden = false; $('askStatus').textContent = 'Answer ready.'; store.write({ questionsAsked: store.read().questionsAsked + 1 });
    } catch (error) { $('askStatus').textContent = error.message || 'Please check the key service and internet connection.'; }
    finally { button.disabled = false; }
  });
})();

const detectForm = document.getElementById('detectForm');
const reviewText = document.getElementById('reviewText');
const ratingSelect = document.getElementById('ratingSelect');
const verifiedCheck = document.getElementById('verifiedCheck');
const duplicateCheck = document.getElementById('duplicateCheck');
const verdictBox = document.getElementById('verdictBox');
const verdictBadge = document.getElementById('verdictBadge');
const severityTag = document.getElementById('severityTag');
const fakeProbVal = document.getElementById('fakeProbVal');
const riskFlagsList = document.getElementById('riskFlagsList');
const runPipelineBtn = document.getElementById('runPipelineBtn');
const refreshFeedBtn = document.getElementById('refreshFeedBtn');
const reviewFeed = document.getElementById('reviewFeed');

// Samples for fast testing
const SAMPLES = {
  bot_praise: {
    text: "AMAZING PRODUCT! BEST HEADPHONES EVER! MUST BUY! A+++++ SELLER! 100% RECOMMEND TO EVERYONE!!",
    rating: 5,
    verified: false,
    duplicate: true
  },
  bot_attack: {
    text: "Scam company terrible product fake do not buy broke immediately refund me worst scam ever",
    rating: 1,
    verified: false,
    duplicate: false
  },
  authentic: {
    text: "I've been using these headphones for two weeks on my daily commute. The active noise cancellation cuts out train noise effectively, though battery life is closer to 24 hours rather than 30. Good purchase overall.",
    rating: 4,
    verified: true,
    duplicate: false
  }
};

function loadSample(key) {
  const sample = SAMPLES[key];
  if (!sample) return;
  reviewText.value = sample.text;
  ratingSelect.value = sample.rating;
  verifiedCheck.checked = sample.verified;
  duplicateCheck.checked = sample.duplicate;
}

// Inspect review form submit
detectForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = reviewText.value.trim();
  if (!text) return;

  try {
    const res = await fetch('/api/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        review_text: text,
        rating: parseInt(ratingSelect.value),
        verified_purchase: verifiedCheck.checked,
        is_duplicate: duplicateCheck.checked
      })
    });

    const data = await res.json();
    if (res.ok) {
      renderVerdict(data);
    } else {
      alert(data.detail || 'Analysis error');
    }
  } catch (err) {
    console.error('Error:', err);
  }
});

function renderVerdict(data) {
  verdictBox.classList.remove('hidden');
  
  verdictBadge.textContent = data.classification.replace(/_/g, ' ');
  verdictBadge.className = 'verdict-badge';
  
  if (data.classification === 'FAKE_BOT_SPAM') {
    verdictBadge.classList.add('badge-fake');
  } else if (data.classification === 'SUSPICIOUS') {
    verdictBadge.classList.add('badge-suspicious');
  } else {
    verdictBadge.classList.add('badge-auth');
  }

  severityTag.textContent = `${data.severity} RISK`;
  fakeProbVal.textContent = `${Math.round(data.fake_probability * 100)}%`;
  fakeProbVal.style.color = data.fake_probability >= 0.65 ? '#ef4444' : (data.fake_probability >= 0.45 ? '#f59e0b' : '#10b981');

  if (data.risk_flags && data.risk_flags.length > 0) {
    riskFlagsList.innerHTML = data.risk_flags.map(f => `<li>⚠️ ${escapeHtml(f)}</li>`).join('');
  } else {
    riskFlagsList.innerHTML = '<li style="border-left-color: #10b981; background: rgba(16, 185, 129, 0.08);">✔ No suspicious anomalies detected. Clean authentic review patterns.</li>';
  }
}

// Run Airflow Pipeline
runPipelineBtn.addEventListener('click', async () => {
  runPipelineBtn.disabled = true;
  runPipelineBtn.textContent = 'Running Airflow Pipeline...';

  try {
    const res = await fetch('/api/run-pipeline', { method: 'POST' });
    const data = await res.json();
    alert(data.message || 'Pipeline complete!');
    loadMetrics();
    loadReviews();
  } catch (err) {
    console.error('Pipeline error:', err);
  } finally {
    runPipelineBtn.disabled = false;
    runPipelineBtn.innerHTML = '<span class="icon">⚡</span> Run Airflow Pipeline';
  }
});

// Load metrics
async function loadMetrics() {
  try {
    const res = await fetch('/api/metrics');
    const data = await res.json();
    document.getElementById('totalReviewsCount').textContent = data.total_reviews;
    document.getElementById('fakeReviewsCount').textContent = data.fake_reviews;
    document.getElementById('suspiciousReviewsCount').textContent = data.suspicious_reviews;
    document.getElementById('authenticReviewsCount').textContent = data.authentic_reviews;
    document.getElementById('fraudRatePct').textContent = `${data.fraud_rate_pct}%`;
  } catch (err) {
    console.error('Metrics error:', err);
  }
}

// Load reviews feed
async function loadReviews() {
  try {
    const res = await fetch('/api/reviews');
    const data = await res.json();
    if (data.reviews.length === 0) {
      reviewFeed.innerHTML = '<div class="feed-placeholder">No reviews audited yet. Click "Run Airflow Pipeline" to process sample batch.</div>';
      return;
    }

    reviewFeed.innerHTML = data.reviews.map(r => `
      <div class="feed-card">
        <div class="feed-meta">
          <strong>${escapeHtml(r.product_name || r.product_id)}</strong>
          <span>⭐ ${r.rating} | ${r.verified_purchase ? '✔ Verified' : '❌ Unverified'}</span>
        </div>
        <p class="feed-text">${escapeHtml(r.review_text)}</p>
        <div class="feed-meta" style="margin-top: 4px;">
          <span style="color: ${r.classification === 'FAKE_BOT_SPAM' ? '#ef4444' : (r.classification === 'SUSPICIOUS' ? '#f59e0b' : '#10b981')}; font-weight: 600;">
            ${r.classification.replace(/_/g, ' ')} (${Math.round(r.fake_probability * 100)}% Risk)
          </span>
          <span>${r.is_quarantined ? '🛑 Quarantined' : 'Allowed'}</span>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Reviews error:', err);
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}

refreshFeedBtn.addEventListener('click', loadReviews);

// Initial Load
document.addEventListener('DOMContentLoaded', () => {
  loadMetrics();
  loadReviews();
});

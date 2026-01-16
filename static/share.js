
// --- SHARE CARD GENERATION ---
const scoreCaptions = {
  "0-10": "ABSOLUTE DISASTER. MY MIRROR CRACKED LOOKING AT THIS.",
  "11-20": "ARE YOU TROLLING ME? BECAUSE THIS FIT IS A JOKE.",
  "21-30": "I'VE SEEN BETTER OUTFITS ON A SCARECROW.",
  "31-40": "BASIC. BORING. BLAND. DO BETTER.",
  "41-50": "MEDIOCRE AT BEST. YOU BLEND INTO THE WALLS.",
  "51-60": "IT'S... FINE. JUST FINE. NOTHING SPECIAL.",
  "61-70": "OKAY, I SEE SOME POTENTIAL. NOT BAD.",
  "71-80": "SOLID FIT. YOU ACTUALLY TRIED TODAY.",
  "81-90": "SHEESH! SOMEONE'S COOKING WITH GAS 🔥",
  "91-100": "GOD TIER DRIP. LEAVE SOME RIZ FOR THE REST OF US 👑"
};

function getCaptionForScore(score) {
  if (score <= 10) return scoreCaptions["0-10"];
  if (score <= 20) return scoreCaptions["11-20"];
  if (score <= 30) return scoreCaptions["21-30"];
  if (score <= 40) return scoreCaptions["31-40"];
  if (score <= 50) return scoreCaptions["41-50"];
  if (score <= 60) return scoreCaptions["51-60"];
  if (score <= 70) return scoreCaptions["61-70"];
  if (score <= 80) return scoreCaptions["71-80"];
  if (score <= 90) return scoreCaptions["81-90"];
  return scoreCaptions["91-100"];
}

async function generateShareCard() {
  const score = parseInt(scoreEl.innerText) || 0;
  const caption = getCaptionForScore(score);

  // Create a temporary canvas for the share card
  const shareCanvas = document.createElement('canvas');
  const ctx = shareCanvas.getContext('2d');

  // Use the saved scanned image
  // Create an image element from the saved data URL
  const img = new Image();

  return new Promise((resolve, reject) => {
    img.onload = function () {
      const srcWidth = img.width;
      const srcHeight = img.height;

      // Set Canvas Size (High Quality, 4:5 Portrait preferred for social, or match source)
      // Let's stick to a solid social media resolution: 1080x1350
      shareCanvas.width = 1080;
      shareCanvas.height = 1350;

      // Fill White Background
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, shareCanvas.width, shareCanvas.height);

      // Draw Image (Cover Fit)
      // Calculate scaling to cover the canvas
      const scale = Math.max(shareCanvas.width / srcWidth, shareCanvas.height / srcHeight);
      const x = (shareCanvas.width / 2) - (srcWidth / 2) * scale;
      const y = (shareCanvas.height / 2) - (srcHeight / 2) * scale;

      ctx.drawImage(img, x, y, srcWidth * scale, srcHeight * scale);

      // Add Overlay Gradient (Bottom fade for text readability)
      const gradient = ctx.createLinearGradient(0, shareCanvas.height * 0.6, 0, shareCanvas.height);
      gradient.addColorStop(0, "transparent");
      gradient.addColorStop(0.8, "rgba(0,0,0,0.9)");
      ctx.fillStyle = gradient;
      ctx.fillRect(0, shareCanvas.height * 0.5, shareCanvas.width, shareCanvas.height * 0.5);

      // Draw Score Circle (Top Right)
      const circleX = shareCanvas.width - 150;
      const circleY = 150;
      const radius = 100;

      ctx.beginPath();
      ctx.arc(circleX, circleY, radius, 0, 2 * Math.PI);
      ctx.fillStyle = "#fff740"; // Sticky Yellow
      ctx.fill();
      ctx.lineWidth = 10;
      ctx.strokeStyle = "#2c2c2c";
      ctx.stroke();

      // Draw Score Text
      ctx.fillStyle = "#2c2c2c";
      ctx.font = "bold 80px 'Patrick Hand', sans-serif"; // Fallback font
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(score, circleX, circleY + 5);

      // Draw Label "DRIP SCORE"
      ctx.fillStyle = "#fff";
      ctx.font = "bold 30px sans-serif";
      ctx.fillText("DRIP SCORE", circleX, circleY + radius + 40);

      // Draw Logo / Watermark (Top Left)
      ctx.fillStyle = "#fff";
      ctx.font = "bold 40px sans-serif";
      ctx.textAlign = "left";
      ctx.fillText("FIT CHECK MIRROR", 50, 80);

      // Draw Caption (Bottom Center)
      ctx.fillStyle = "#fff740"; // Yellow pop
      ctx.font = "bold 60px 'Patrick Hand', sans-serif";
      ctx.textAlign = "center";

      // Wrap Text Logic
      const maxWidth = shareCanvas.width - 100;
      const lineHeight = 70;
      const lineY = shareCanvas.height - 250;

      function wrapText(context, text, x, y, maxWidth, lineHeight) {
        var words = text.split(' ');
        var line = '';

        for (var n = 0; n < words.length; n++) {
          var testLine = line + words[n] + ' ';
          var metrics = context.measureText(testLine);
          var testWidth = metrics.width;
          if (testWidth > maxWidth && n > 0) {
            context.fillText(line, x, y);
            line = words[n] + ' ';
            y += lineHeight;
          }
          else {
            line = testLine;
          }
        }
        context.fillText(line, x, y);
      }

      wrapText(ctx, caption, shareCanvas.width / 2, lineY, maxWidth, lineHeight);

      // Download
      const link = document.createElement('a');
      link.download = `drip-check-${Date.now()}.png`;
      link.href = shareCanvas.toDataURL();
      link.click();

      // Show confirmation popup
      setTimeout(() => {
        showCustomAlert('DRIP CARD DOWNLOADED! 📥 CHECK YOUR DOWNLOADS FOLDER!', '🎉 HURRAY! 🎉', 'GOT IT! 👍');
      }, 300); // Small delay to ensure download starts first

      resolve();
    };

    img.onerror = reject;

    // Load the saved scanned image
    img.src = scannedImageDataUrl;
  });
}

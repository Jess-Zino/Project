// mathml-to-speech.js
const sre = require("speech-rule-engine");
function cleanSpeech(text) {
  return (
    text
      // Derivatives
      .replace(
        /StartFraction d squared y Over d x squared EndFraction/gi,
        "the second derivative of y with respect to x"
      )
      .replace(
        /StartFraction d squared (.*?) Over d (.*?) squared EndFraction/gi,
        "the second derivative of $1 with respect to $2"
      )
      .replace(
        /StartFraction d (.*?) Over d (.*?) EndFraction/gi,
        "the derivative of $1 with respect to $2"
      )

      // Fractions
      .replace(/StartFraction/g, "the fraction ")
      .replace(/EndFraction/g, "")
      .replace(/Over/g, " over ")

      // Roots
      .replace(/StartRoot/g, "the square root of ")
      .replace(/EndRoot/g, "")
      .replace(/NthRoot\((\d+),\s*(.*?)\)/gi, "the $1th root of $2")

      // Powers and subscripts
      .replace(/Superscript/g, " to the power of ")
      .replace(/Subscript/g, " subscript ")

      // Operations
      .replace(/\bplus\b/gi, " plus ")
      .replace(/\bminus\b/gi, " minus ")
      .replace(/\btimes\b/gi, " times ")
      .replace(/\bdivided by\b/gi, " divided by ")
      .replace(/\bequals\b/gi, " is equal to ")
      .replace(/\bnot equals\b/gi, " is not equal to ")
      .replace(
        /\bgreater than or equal to\b/gi,
        " is greater than or equal to "
      )
      .replace(/\bless than or equal to\b/gi, " is less than or equal to ")
      .replace(/\bgreater than\b/gi, " is greater than ")
      .replace(/\bless than\b/gi, " is less than ")

      // Trigonometry
      .replace(/\bsin\b/gi, "sine of ")
      .replace(/\bcos\b/gi, "cosine of ")
      .replace(/\btan\b/gi, "tangent of ")
      .replace(/\bcot\b/gi, "cotangent of ")
      .replace(/\bsec\b/gi, "secant of ")
      .replace(/\bcsc\b/gi, "cosecant of ")

      // Logs & Exponentials
      .replace(/\bln\b/gi, "natural logarithm of ")
      .replace(/\blog\b/gi, "logarithm of ")
      .replace(/\bexp\b/gi, "exponential of ")

      // Integrals & summation
      .replace(
        /integral from (.*?) to (.*?) of/gi,
        "the integral from $1 to $2 of"
      )
      .replace(/StartSummation/gi, "the summation of ")
      .replace(/EndSummation/gi, "")
      // Indefinite integral
      .replace(
        /\\int\s*(.*?)\s*\\,?\s*d\s*(\w)/gi,
        "integral of $1 with respect to $2"
      )
      // Basic partial derivative

      // Absolute and modulus
      .replace(/modulus of/gi, "the modulus of ")
      .replace(/\|(.+?)\|/g, "the absolute value of $1")

      .replace(
        /\StartAbsoluteValue(.+?)\EndAbsoluteValue/g,
        "the absolute value of $1"
      )

      // Greek letters (both lower and upper case)
      .replace(/\balpha\b/gi, "alpha")
      .replace(/\bbeta\b/gi, "beta")
      .replace(/\bgamma\b/gi, "gamma")
      .replace(/\bdelta\b/gi, "delta")
      .replace(/\bepsilon\b/gi, "epsilon")
      .replace(/\bzeta\b/gi, "zeta")
      .replace(/\beta\b/gi, "beta")

      // Extra common Greek symbols
      .replace(/\btheta\b/gi, "theta")
      .replace(/\blambda\b/gi, "lambda")
      .replace(/\bkappa\b/gi, "kappa")
      .replace(/\bmu\b/gi, "mu")
      .replace(/\bnu\b/gi, "nu")
      .replace(/\bxi\b/gi, "xi")
      .replace(/\bomicron\b/gi, "omicron")
      .replace(/\bpi\b/gi, "pi")
      .replace(/\brho\b/gi, "rho")
      .replace(/\bsigma\b/gi, "sigma")
      .replace(/\btau\b/gi, "tau")
      .replace(/\bupsilon\b/gi, "upsilon")
      .replace(/\bphi\b/gi, "phi")
      .replace(/\bchi\b/gi, "chi")
      .replace(/\bpsi\b/gi, "psi")
      .replace(/\bomega\b/gi, "omega")

      // Sets and matrices
      .replace(/StartSet/g, "the set of ")
      .replace(/EndSet/g, "")
      .replace(/matrix/gi, "a matrix")
    
      // Clean-up
      .replace(/\s+/g, " ")
      .trim()
        .replace(
        /the fraction partial differential (\w+) over partial differential (upper )?(\w+)/gi,
        "partial derivative of $1 with respect to $3"
      )
        .replace(
        /\\frac\s*{\\partial\s*(\w+)}\s*{\\partial\s*(\w+)}/gi,
        "partial derivative of $1 with respect to $2"
      )

      // Second order partial derivative with powers
      .replace(
        /\\frac\s*{\\partial\^(\d+)\s*(\w+)}\s*{\\partial\s*(\w+)\^(\d+)}/gi,
        "$1th partial derivative of $2 with respect to $3 to the power $4"
      )
      .replace(/\b(\d(?:\s+\d)+)\b/g, (match) => {
        return match.replace(/\s+/g, '');
      })


      // ordinary derivative
      .replace(
        /the fraction d (\w+) over d (upper )?(\w+)/gi,
        "derivative of $1 with respect to $3"
      )

      // variation (delta)
      .replace(
        /the fraction delta (\w+) over delta (upper )?(\w+)/gi,
        "variation of $1 with respect to $3"
      )
      
      // Mixed partial derivatives (second order)
      .replace(
        /\\frac\s*{\\partial\^2\s*(\w+)}\s*{\\partial\s*(\w+)\s*\\partial\s*(\w+)}/gi,
        "second mixed partial derivative of $1 with respect to $2 and $3"
      )

      // Definite integral with limits
      .replace(
        /\\int_([^\^]+)\^([^\s]+)\s*(.*?)\s*\\,?\s*d\s*(\w)/gi,
        "integral from $1 to $2 of $3 with respect to $4"
      )
          .replace(/\bStartLayout\b/g, "")
    .replace(/\bEndLayout\b/g, "")
    
    // Remove all numbered rows like "1st Row", "2nd Row", etc.
    .replace(/\b\d+(st|nd|rd|th)\s+Row\b/g, "")
    
    // Optional: remove extra spaces
    .replace(/\s{2,}/g, " ")

  );
}

async function main() {
  await sre.setupEngine({
    locale: "en",
    speech: "sre",
  });

  const mathml = process.argv[2];
  if (!mathml) {
    console.error("Please provide MathML input as an argument.");
    process.exit(1);
  }

  let spoken = sre.toSpeech(mathml, {
    domain: "math",
    style: "clearspeak", // use clearspeak style for friendlier output
    modality: "speech",
  });

  spoken = cleanSpeech(spoken);

  console.log(spoken);
}

main().catch(console.error);

// const BASE_URL = window.location.hostname.includes("mailmeteor") ? 'https://tools.mailmeteor.com' : 'http://localhost:8080';
const BASE_URL = 'https://tools.mailmeteor.com'

const CHECKS_MAPPING = {
  format: {
    title: 'Format',
    valid: () => `This email address is written correctly and isn't gibberish.`,
    invalid: () => `The email address isn't written in a valid format.`,
    skipped: () => `We didn't verify that the email address follows standard formatting rules.`
  },
  disposable: {
    title: 'Professional',
    valid: () => `The domain isn't linked to webmail or throwaway email services.`,
    invalid: () => `The domain is known for offering temporary or disposable email addresses.`,
    risky: () => `The domain is known for offering temporary or disposable email addresses.`,
    skipped: () => `We didn't check whether the domain is disposable.`
  },
  domain_status: {
    title: 'Domain status',
    valid: () => 'The domain name exists and has valid MX records.',
    invalid: () => 'The domain name does not exist or is missing MX records.',
    skipped: () => `We didn't verify if the domain can receive email.`
  },
  smtp: {
    title: 'Mailbox',
    valid: () => 'The mail server responded and confirmed that this mailbox exists.',
    invalid: () => `The mail server is unreachable or it says this mailbox doesn't exist.`,
    skipped: () => `We didn't ask the mail server about this mailbox.`,
    unknown: (reason) => {
      const reasonMessages = {
        'catch_all_mailbox': `This domain accepts every email address (catch-all), so we can't tell if this specific one exists.`,
      };

      return reasonMessages[reason] || `The mailbox might exist, but we can't confirm it.`;
    }
  }
}

Vue.component('result-header', {
  props: {
    status: {
      validator(value) {
        return ['valid', 'loading', 'invalid', 'unknown', 'failure', 'risky'].includes(value)
      }
    },
    email: String,
  },

  computed: {
    imageSrc() {
      if (!this.status || this.status === 'failure') {
        return '/assets/img/tools/email-checker-invalid.svg'
      }

      return `/assets/img/tools/email-checker-${this.status}.svg?version=20250610`
    }
  },

  template: `<div class="result-header">
  <img height="62" :src="imageSrc" width="62">
  <div class="ml-4">
    <template v-if="status === 'loading'">
      <h3 class="loading">Checking<span>.</span><span>.</span><span>.</span></h3>
      <p></p>
    </template>
    <template v-else-if="status === 'valid'">
      <h3>Valid</h3>
      <p class="break-word">{{ email }} is a valid email address</p>
    </template>
    <template v-else-if="status === 'invalid'">
      <h3>Invalid</h3>
      <p class="break-word">{{ email }} is not a valid email address</p>
    </template>
    <template v-else-if="status === 'risky'">
      <h3>Risky</h3>
      <p class="break-word">{{ email }} might be risky to send an email to</p>
    </template>
    <template v-else-if="status === 'unknown'">
      <h3>Unknown</h3>
      <p class="break-word">{{ email }} might exist, but we can't confirm it</p>
    </template>
    <template v-else>
      <h3>Something went wrong</h3>
      <p>Unable to verify email. Please try again.</p>
    </template>
  </div>
</div>`
})

Vue.component('result-details-item', {
  props: {
    title: String,
    status: {
      validator(value) {
        return ['valid', 'invalid', 'risky', 'unknown', 'skipped'].includes(value.toString().toLowerCase())
      }
    },
    explanation: String
  },
  computed: {
    badgeClass() {
      switch (this.status) {
        case 'valid':
          return 'badge-success'
        case 'invalid':
          return 'badge-danger'
        case 'risky':
          return 'badge-danger'
        case 'unknown':
          return 'badge-secondary'
        case 'skipped':
          return 'badge-secondary'
        default:
          return 'badge-secondary'
      }
    },
  },
  template: `
      <div class="result-details-item">
        <div class="d-flex mb-1">
          <span class="mr-2">{{ title }}</span>
          <span :class="['badge', badgeClass, 'font-weight-normal', 'align-self-center']">{{ this.status }}</span>
        </div>
        <div class="result-detail-item-explanation">
          {{ explanation }}
        </div>
      </div>
    `
});

const emailChecker = new Vue({
  el: '#email-checker',
  data: {
    status: 'idle',
    email: '',
    result: null,
    examples: [
      "elon@spacex.com",
      "invalid@mailmeteor.com",
      "pablo@picasso",
      "thisemaildoesnotexists@email.example"
    ],
  },

  mounted() {
    this.$nextTick(() => {
      this.initializeTooltips()
      this.checkQueryParamAndGenerate()
      this.resultTextarea = this.$refs.resultTextarea

      try {
        const emailInput = document.getElementById('email-to-check')
        if (emailInput) {
          emailInput.addEventListener('input', () => {
            if (emailInput.value && this.isValidEmail(emailInput.value)) {
              emailInput.classList.remove('is-invalid')
            }
          })
        }
      } catch (_) {  }
    })
  },

  updated() {
    this.$nextTick(() => {
      this.initializeTooltips()
    })
  },

  methods: {
    initializeTooltips() {
      try {
        if (typeof $ === 'undefined' || !$.fn || !$.fn.tooltip) {
          setTimeout(this.initializeTooltips, 100);
          return;
        }

        $('[data-toggle="tooltip"]').tooltip('dispose');
        $('[data-toggle="tooltip"]').tooltip({ container: 'body' });
      } catch (_) { }
    },
    onSubmit() {
      if (this.validateInputs()) {
        this.checkEmail()
      }
    },

    isValidEmail(email) {
      return (email || '').trim().includes('@')
    },

    validateInputs() {
      const email = (this.email || '').trim()

      const valid = !!email && this.isValidEmail(email)
      if (!valid) {
        document.getElementById('email-to-check').classList.add('is-invalid')
      }
      return valid
    },

    /**
     * Transforms domain-related checks (DNS + MX) into a single domain_status
     */
    transformDomainCheck(dnsCheck, mxCheck) {
      const dnsStatus = dnsCheck.status
      const mxStatus = mxCheck.status

      let status = 'skipped'
      let reason = null

      // Handle status
      if (dnsStatus === 'invalid' || mxStatus === 'invalid') {
        status = 'invalid'
      } else if (dnsStatus === 'valid' && mxStatus === 'valid') {
        status = 'valid'
      }

      // Handle reason
      reason = dnsCheck.reason || mxCheck.reason

      return { status, reason }
    },

    /**
     * Transforms the raw API response checks into the format expected by the UI
     */
    transformChecks(apiChecks) {
      return {
        ...apiChecks,
        domain_status: this.transformDomainCheck(apiChecks.dns, apiChecks.mx),
      }
    },

    async checkEmail() {
      this.updateQueryParam()
      this.status = "loading"
      this.result = null

      try {
        // Retrieve captcha
        const captchaToken = await this.captcha()

        // Call the API
        const response = await fetch(`${BASE_URL}/api/email-checker?cf-turnstile-response=${captchaToken}`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            email: this.email,
          }),
        });

        // Parse the response
        if (response.ok) {
          const jsonResponse = await response.json()

          this.result = {
            email: jsonResponse.email,
            status: jsonResponse.status,
            checks: []
          }

          // Transform checks before mapping to UI format
          const transformedChecks = this.transformChecks(jsonResponse.checks)

          this.result.checks = Object.entries(CHECKS_MAPPING).map(([key, config]) => {
            const { status, reason } = transformedChecks[key];
            const explanation = config[status](reason);

            return {
              title: config.title,
              status,
              explanation
            };
          });

          this.status = this.result.status

          // Analytics
          gtag('event', 'tool', {
            'event_category': 'engagement',
            'event_label': 'email_checker:verify',
            'value': 1
          });

          // Promote the Google Sheets add-on
          this.handlePromotion();
        } else {
          throw new Error('Empty error')
        }

      } catch (error) {
        console.error(error)
        console.error('Error submitting instructions:', error);
        this.status = "failure"
      }
    },

    captcha() {
      return new Promise(function (resolve, reject) {
        turnstile.render('#cloudflare-captcha', {
          sitekey: '0x4AAAAAAAe7i7oicz-TnMTr',
          action: 'emailchecker',
          callback: function (token) {
            resolve(token)
          },
          'error-callback': function (err) {
            reject(err)
          }
        });
      })
    },

    updateQueryParam() {
      const encodedPrompt = encodeURIComponent(this.email)
      const newUrl = `${window.location.pathname}?email=${encodedPrompt}`
      history.pushState({path: newUrl}, '', newUrl)
    },

    checkQueryParamAndGenerate() {
      const urlParams = new URLSearchParams(window.location.search)
      const promptParam = urlParams.get('email')
      if (promptParam) {
        this.email = decodeURIComponent(promptParam)
        this.onSubmit()
      }
    },

    handlePromotion() {
      try {
        const MODAL_ID = '#modal-email-checker-promotion';
        const LS_VERIFICATION_COUNT_KEY = 'tools.email_checker.verification.count';
        const LS_MODAL_TIMESTAMP_KEY = 'tools.email_checker.verification.last_shown';
        const MODAL_DISPLAY_FREQUENCY = 5;
        const ONE_DAY_IN_MS = 24 * 60 * 60 * 1000;

        let count = parseInt(localStorage.getItem(LS_VERIFICATION_COUNT_KEY) || '0');
        count++;
        localStorage.setItem(LS_VERIFICATION_COUNT_KEY, count.toString());

        const shouldDisplayModal = (count > 0) && ((count % MODAL_DISPLAY_FREQUENCY) === 0);

        if (!shouldDisplayModal) {
          return
        }

        const lastShown = parseInt(localStorage.getItem(LS_MODAL_TIMESTAMP_KEY) || '0');
        const now = new Date().getTime();

        const hasModalBeenSeenToday = (now - lastShown) < ONE_DAY_IN_MS;

        if (!hasModalBeenSeenToday) {
            $(MODAL_ID).modal('show');
            localStorage.setItem(LS_MODAL_TIMESTAMP_KEY, now.toString());
        }
      } catch (error) {
        /* do nothing */
      }
    }
  },
});

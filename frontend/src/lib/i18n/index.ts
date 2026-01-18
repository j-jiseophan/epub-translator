import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';
import { translations, type Locale, type TranslationKeys } from './translations';

const STORAGE_KEY = 'epub-translator-locale';
const SUPPORTED_LOCALES: Locale[] = ['ko', 'en'];

function getSystemLocale(): Locale {
	if (!browser) return 'en';
	const lang = navigator.language.split('-')[0];
	return SUPPORTED_LOCALES.includes(lang as Locale) ? (lang as Locale) : 'en';
}

function getInitialLocale(): Locale | 'system' {
	if (!browser) return 'system';
	const saved = localStorage.getItem(STORAGE_KEY);
	if (saved === 'system' || saved === null) return 'system';
	if (SUPPORTED_LOCALES.includes(saved as Locale)) return saved as Locale;
	return 'system';
}

function createLocaleStore() {
	const { subscribe, set, update } = writable<Locale | 'system'>(getInitialLocale());

	return {
		subscribe,
		set: (value: Locale | 'system') => {
			if (browser) {
				localStorage.setItem(STORAGE_KEY, value);
			}
			set(value);
		},
		toggle: () => {
			update((current) => {
				const resolved = current === 'system' ? getSystemLocale() : current;
				const next = resolved === 'ko' ? 'en' : 'ko';
				if (browser) {
					localStorage.setItem(STORAGE_KEY, next);
				}
				return next;
			});
		}
	};
}

export const localePreference = createLocaleStore();

export const locale = derived(localePreference, ($pref) => {
	return $pref === 'system' ? getSystemLocale() : $pref;
});

export const t = derived(locale, ($locale) => {
	return translations[$locale];
});

export function getTranslation(): TranslationKeys {
	return translations[get(locale)];
}

export { translations, type Locale, type TranslationKeys };

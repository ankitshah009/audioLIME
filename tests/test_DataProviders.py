import unittest
from audioLIME.data_provider import DataProvider, RawAudioProvider, NusslAudioProvider
import tempfile
import librosa
import numpy as np


class DummyDataProvider(DataProvider):
    def __init__(self, audio_path):
        super().__init__(audio_path)

    def initialize_mix(self):
        return None


class TestDataProviders(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sr = 16000
        self.temp_signal = np.random.randn(self.sr * 3) # create "fake" signal with 3 seconds length
        # self.reference_signal_resampled = \
        #     librosa.resample(librosa.resample(self.temp_signal, self.sr, 41000), 41000, self.sr)  # otherwise they won't be equal
        self.tmpfile = tempfile.NamedTemporaryFile()
        self.audio_path = self.tmpfile.name
        librosa.output.write_wav(self.audio_path, self.temp_signal, self.sr)
        self.decimal_places = 5

    def test_BaseDataProvider(self):
        self.assertRaises(NotImplementedError, DataProvider, self.audio_path)

    def test_AudioPath(self):
        dp = DummyDataProvider(self.audio_path)
        self.assertEqual(self.audio_path, dp.get_audio_path())

    def test_RawAudioProviderMix(self):
        dp = RawAudioProvider(self.audio_path)
        print("mix", dp.get_mix())
        print("ref", self.temp_signal)
        self.assertTrue(np.allclose(dp.get_mix(), self.temp_signal, atol=10**self.decimal_places))

    def test_NusslAudioProviderMix(self):
        dp = NusslAudioProvider(self.audio_path)
        self.assertTrue(np.allclose(dp.get_mix().audio_data, self.temp_signal, atol=10**self.decimal_places))

    def test_RawAudioAnalysisWindow(self):
        dp = RawAudioProvider(self.audio_path)
        start = 32000
        leng = 16000
        dp.set_analysis_window(start, leng)
        mix = dp.get_mix()
        self.assertAlmostEqual(mix[0], self.temp_signal[start], places=self.decimal_places)
        self.assertAlmostEqual(mix[-1], self.temp_signal[-1], places=self.decimal_places)
        self.assertEqual(len(mix), leng)
        self.assertTrue(np.allclose(dp._original_mix, self.temp_signal, atol=10**self.decimal_places))

    def test_NusslAudioAnalysisWindow(self):
        dp = NusslAudioProvider(self.audio_path)
        start = 32000
        leng = 16000
        dp.set_analysis_window(start, leng)
        mix = dp.get_mix().audio_data[0]  # nested
        self.assertAlmostEqual(mix[0], self.temp_signal[start], places=self.decimal_places)
        self.assertAlmostEqual(mix[-1], self.temp_signal[-1], places=self.decimal_places)
        self.assertEqual(len(mix), leng)
        self.assertTrue(np.allclose(dp._original_mix.audio_data, self.temp_signal, atol=10**self.decimal_places))

if __name__ == '__main__':
    unittest.main()
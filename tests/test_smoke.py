"""Hızlı, dış servis gerektirmeyen regresyon testleri."""

import io
import os
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dashboard"))

import app as dashboard_app  # noqa: E402


class DashboardSmokeTests(unittest.TestCase):
    def setUp(self):
        dashboard_app.app.config["TESTING"] = True

    def test_upload_rejects_wrong_embedding_shape(self):
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.dict(
            os.environ,
            {"UPLOAD_TOKEN": "test-token", "EMBEDDINGS_INCOMING_DIR": temp_dir},
            clear=False,
        ):
            payload = io.BytesIO()
            np.save(payload, np.zeros((2, 10), dtype=np.float32))
            payload.seek(0)
            with dashboard_app.app.test_client() as client:
                response = client.post(
                    "/api/upload-embedding",
                    data={"file": (payload, "bad.npy")},
                    headers={"Authorization": "Bearer test-token"},
                    content_type="multipart/form-data",
                )
            self.assertEqual(response.status_code, 400)
            self.assertFalse(os.path.exists(os.path.join(temp_dir, "mpnet_multilingual_embeddings_100k.npy")))

    def test_plot_reports_missing_umap(self):
        frame = pd.DataFrame({"external_id": ["1"], "risk_skoru": [0.4], "hdbscan_kume": [0]})
        with mock.patch.object(dashboard_app, "load_algorithm_data", return_value=frame):
            with dashboard_app.app.test_client() as client:
                response = client.get("/api/plot?algorithm=hdbscan")
        self.assertEqual(response.status_code, 503)
        self.assertIn("UMAP", response.get_json()["error"])

    def test_risk_and_cluster_plot_modes_are_distinct(self):
        frame = pd.DataFrame(
            {
                "external_id": ["1", "2"],
                "risk_skoru": [0.2, 0.8],
                "hdbscan_kume": [3, -1],
                "forced_cluster": [3, 7],
                "forced_strength": [0.0, 0.4],
                "umap_x": [1.0, 2.0],
                "umap_y": [1.0, 2.0],
            }
        )
        with mock.patch.object(dashboard_app, "load_algorithm_data", return_value=frame):
            with dashboard_app.app.test_client() as client:
                risk = client.get("/api/plot?algorithm=hdbscan&view=risk").get_json()
                cluster = client.get("/api/plot?algorithm=hdbscan&view=cluster").get_json()

        self.assertTrue(risk["data"][0]["marker"]["showscale"])
        self.assertFalse(cluster["data"][0]["marker"]["showscale"])
        self.assertEqual(cluster["data"][0]["marker"]["color"][1], "#dc2626")
        self.assertEqual(cluster["data"][0]["marker"]["size"][1], 10)

    def test_cluster_view_keeps_both_original_and_soft_assignments(self):
        """API, istemcinin iki görselleştirme modunu seçebilmesi için iki etiketi taşır."""
        frame = pd.DataFrame(
            {
                "external_id": ["1", "2"],
                "risk_skoru": [0.2, 0.8],
                "hdbscan_kume": [3, -1],
                "forced_cluster": [3, 7],
                "forced_strength": [0.0, 0.4],
                "umap_x": [1.0, 2.0],
                "umap_y": [1.0, 2.0],
            }
        )
        with mock.patch.object(dashboard_app, "load_algorithm_data", return_value=frame):
            with dashboard_app.app.test_client() as client:
                response = client.get("/api/plot?algorithm=hdbscan&view=cluster")

        records = response.get_json()["data"][0]["customdata"]
        self.assertEqual(records[1]["kume"], -1)
        self.assertEqual(records[1]["forced_cluster"], 7)


if __name__ == "__main__":
    unittest.main()

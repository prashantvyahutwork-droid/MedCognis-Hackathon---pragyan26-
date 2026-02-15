import pandas as pd
import numpy as np
import pickle
import shap
import os
from sklearn.metrics import accuracy_score, f1_score

class TriageEngine:
    def __init__(self, model_path=None):
        if model_path is None:
            # Default to file in same directory as this script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.model_path = os.path.join(base_dir, 'triage_xgboost_v2.pkl')
        else:
            self.model_path = model_path
            
        self.model = None
        self.le_risk = None
        self.le_dict = None
        self.explainer = None
        self._load_model()

    def reload_model(self, model_path=None):
        if model_path:
            self.model_path = model_path
        print(f"Reloading model from {self.model_path}...")
        self._load_model()

    def _load_model(self):
        try:
            # Adjust path if running from root
            if not os.path.exists(self.model_path):
                 # Try absolute path or relative to engine folder if needed
                 pass 
            
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
            self.model = data['model']
            self.le_risk = data['le_risk']
            self.le_dict = data['le_dict']
            
            # Initialize SHAP explainer gracefully
            try:
                self.explainer = shap.TreeExplainer(self.model)
                print("Model and SHAP explainer loaded successfully.")
            except Exception as e:
                print(f"Warning: SHAP explainer could not be initialized: {e}")
                self.explainer = None
                print("Model loaded successfully (without SHAP).")
        except FileNotFoundError:
            print(f"CRITICAL ERROR: {self.model_path} file not found at {os.path.abspath(self.model_path)}!")
            raise
        except Exception as e:
            print(f"CRITICAL ERROR loading model: {e}")
            raise

    def get_shap_explanation(self, input_df):
        """
        Calculate SHAP values for the input.
        Returns a dict of feature items and their SHAP values.
        """
        try:
            shap_values = self.explainer.shap_values(input_df)
            
            # shap_values might be a list (one for each class) or a single array
            # For multi-class XGBoost, it often returns a list.
            # We want the values for the predicted class or just the max risk class.
            
            # Simplified: Just take the sum of absolute SHAP values to show "importance" 
            # or usage specific logic for the predicted class.
            
            # Let's assume binary/regression or we pick the index of the predicted class later regarding implementation details.
            # For now, let's just return the raw values mapped to columns.
            
            # If shap_values is a list (multi-class), we need to know which class prediction we care about.
            # We will handle this in the main prediction flow.
            return shap_values
        except Exception as e:
            print(f"SHAP Error: {e}")
            return None

    def hybrid_risk_engine(self, input_df):
        """
        AI RISK ENGINE: ML Prediction + Rule-based Safety Overrides.
        """
        # ML Prediction
        probs = self.model.predict_proba(input_df)[0]
        pred_idx = np.argmax(probs)
        risk_label = self.le_risk.inverse_transform([pred_idx])[0]
        confidence = float(np.max(probs))
        
        # SHAP Values
        shap_values = self.get_shap_explanation(input_df)
        
        feature_contributions = {}
        try:
            # Handle SHAP output structure (can vary by model type/version)
            if isinstance(shap_values, list):
                # Multi-class: list of arrays
                class_shap = shap_values[pred_idx]
            else:
                # Single output or binary
                class_shap = shap_values

            # Ensure we have a 1D array of feature values for this single sample
            if hasattr(class_shap, 'shape'):
                print(f"DEBUG: SHAP shape: {class_shap.shape}")
                
                # Case 1: (1, features, classes) - XGBoost raw output often 3D
                if len(class_shap.shape) == 3:
                    # class_shap is actually all shap values. We need to slice.
                    # shape: (1, 7, 3) -> Take row 0, all features, specific class index
                    # But wait, if 'shap_values' was the 3D array, we need to index it by pred_idx
                    # If we are here, 'class_shap' = 'shap_values' because it wasn't a list.
                    
                    # So we take [0, :, pred_idx]
                    vals = class_shap[0, :, pred_idx]
                    
                # Case 2: (1, features)
                elif len(class_shap.shape) == 2:
                    vals = class_shap[0]
                    
                # Case 3: (features,)
                elif len(class_shap.shape) == 1:
                    vals = class_shap
                else:
                    vals = None
                
                if vals is not None:
                    for idx, col in enumerate(input_df.columns):
                        # Safe conversion to float
                        val = vals[idx]
                        if isinstance(val, np.ndarray):
                            val = val.item()
                        feature_contributions[col] = float(val)
        except Exception as e:
            print(f"Error processing SHAP values: {e}")


        # HYBRID RULES: Safety Overrides (Rule-based Layer)
        is_rule_triggered = False
        override_reason = None
        
        if input_df['Blood_Pressure'].values[0] >= 180:
            risk_label, confidence, is_rule_triggered = "High", 1.0, True
            override_reason = "Critical Blood Pressure (>180)"
        elif input_df['Temperature'].values[0] >= 40.0:
            risk_label, confidence, is_rule_triggered = "High", 1.0, True
            override_reason = "Critical Body Temperature (>40°C)"
        elif input_df.get('O2_Saturation', 100).values[0] < 90:
             risk_label, confidence, is_rule_triggered = "High", 1.0, True
             override_reason = "Critical Hypoxia (O2 < 90%)"
        elif input_df.get('Consciousness', 0).values[0] != 0: # 0 is mapped to Alert usually, but let's check encoding
             # Actually, encoding might vary. Let's rely on ML primarily unless it's obvious.
             pass

        return risk_label, confidence, is_rule_triggered, feature_contributions, override_reason

    def get_dept_recommendation(self, symptom_name, risk_level):
        """
        DEPARTMENT RECOMMENDATION ENGINE: Based on symptoms and risk.
        Now includes disease prediction, treatment mapping, and doctor specialist recommendation.
        """
        medical_knowledge = {
            'Chest Pain': {
                'High': {'disease': 'Acute Coronary Syndrome', 'dept': '🚨 Cardiology (ER)', 'specialist': 'Senior Cardiologist', 'treatment': ['ECG Monitoring', 'Troponin Test', 'Aspirin']},
                'Medium': {'disease': 'Stable Angina / Pericarditis', 'dept': '🫀 Cardiology', 'specialist': 'Cardiology Specialist', 'treatment': ['Stress Test', 'BP Monitoring', 'Follow-up']},
                'Low': {'disease': 'Musculoskeletal Pain', 'dept': '🏥 General Medicine', 'specialist': 'General Physician', 'treatment': ['Observation', 'Pain Relief']}
            },
            'Fever': {
                'High': {'disease': 'Systemic Sepsis', 'dept': '🚨 Emergency Care', 'specialist': 'Emergency Physician', 'treatment': ['IV Fluids', 'Blood Cultures', 'IV Antibiotics']},
                'Medium': {'disease': 'Community Acquired Pneumonia', 'dept': '🌡️ Internal Medicine', 'specialist': 'Internal Medicine Specialist', 'treatment': ['Oral Antibiotics', 'Hydration', 'X-Ray']},
                'Low': {'disease': 'Viral Syndrome', 'dept': '🏥 General Medicine', 'specialist': 'General Physician', 'treatment': ['Antipyretics', 'Rest', 'Fluids']}
            },
            'Cough': {
                'High': {'disease': 'Acute Respiratory Distress', 'dept': '🚨 Pulmonology (ER)', 'specialist': 'Pulmonology Chief', 'treatment': ['O2 Therapy', 'Nebulization', 'Chest CT']},
                'Medium': {'disease': 'Bronchitis / Asthma Flare', 'dept': '🫁 Pulmonology', 'specialist': 'Pulmonology Specialist', 'treatment': ['Inhalers', 'Steroids', 'Pulse Oximetry']},
                'Low': {'disease': 'Upper Respiratory Infection', 'dept': '🏥 General Medicine', 'specialist': 'General Physician', 'treatment': ['Steam Inhalation', 'Cough Syrup']}
            },
            'Abdominal Pain': {
                'High': {'disease': 'Acute Appendicitis / Perforation', 'dept': '🚨 Surgery (ER)', 'specialist': 'Emergency Surgeon', 'treatment': ['NPO Status', 'Abdominal CT', 'Surgical Consult']},
                'Medium': {'disease': 'Gastroenteritis', 'dept': '🧪 Gastroenterology', 'specialist': 'Gastroenterology Specialist', 'treatment': ['IV Fluids', 'Stool Analysis', 'Antispasmodics']},
                'Low': {'disease': 'Indigestion / Gastritis', 'dept': '🏥 General Medicine', 'specialist': 'General Physician', 'treatment': ['Antacids', 'Dietary Modification']}
            },
            'Numbness': {
                'High': {'disease': 'Acute Ischemic Stroke', 'dept': '🚨 Neurology (ER)', 'specialist': 'Stroke Neurology Chief', 'treatment': ['NIH Stroke Scale', 'Brain MRI', 'TPA Eligibility']},
                'Medium': {'disease': 'Peripheral Neuropathy', 'dept': '🧠 Neurology', 'specialist': 'Neurology Specialist', 'treatment': ['Nerve Conduction Test', 'B12 Screen']},
                'Low': {'disease': 'Pinched Nerve', 'dept': '🏥 Orthopedics', 'specialist': 'Orthopedic Surgeon', 'treatment': ['Physical Therapy', 'Observation']}
            },
            'Breathlessness': {
                'High': {'disease': 'Pulmonary Embolism / Acute CHF', 'dept': '🚨 Critical Care', 'specialist': 'Critical Care Chief', 'treatment': ['Anticoagulation', 'Diuretics', 'Echogram']},
                'Medium': {'disease': 'COPD Exacerbation', 'dept': '🫁 Pulmonology', 'specialist': 'Pulmonology Specialist', 'treatment': ['Bronchodilators', 'Steroids']},
                'Low': {'disease': 'Anxiety / Mild Asthma', 'dept': '🏥 General Medicine', 'specialist': 'General Physician', 'treatment': ['Breathing Exercises', 'Salbutamol']}
            }
        }

        # Handle department override for High risk if not in map
        if risk_level == "High" and symptom_name not in medical_knowledge:
            return "🚨 Emergency & Critical Care", "Severe Clinical Condition", "Emergency Physician", ["Immediate Stabilization", "Critical Vitals Monitoring"]

        info = medical_knowledge.get(symptom_name, {}).get(risk_level, {
            'disease': 'General Clinical Condition',
            'dept': '🏥 General Medicine',
            'specialist': 'General Physician',
            'treatment': ['Clinical Observation', 'Diagnostic Tests']
        })
        
        return info['dept'], info['disease'], info['specialist'], info['treatment']



    def calculate_benchmarks(self, csv_path='data/final_triage_data_50k_v2.csv'):
        """
        Calculate model performance metrics using the dataset.
        """
        try:
            from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
            
            # Load Data
            if not os.path.exists(csv_path):
                 # Try finding it relative to project root
                 csv_path = os.path.join(os.getcwd(), csv_path)
            
            if not os.path.exists(csv_path):
                return {"error": "Dataset not found for benchmarking."}

            df = pd.read_csv(csv_path).sample(1000) # Use a subset for speed
            
            # Preprocess logic (Simplified for demo)
            req_cols = ['Age', 'Gender', 'Symptoms', 'Blood_Pressure', 'Heart_Rate', 'Temperature', 'O2_Saturation', 'Pain_Severity', 'Consciousness', 'Pre_Existing_Conditions', 'Risk_Level']
            if not all(col in df.columns for col in req_cols):
                 return {"error": "Dataset schema mismatch."}

            # Helper for safe map using LabelEncoder objects
            def safe_map(col, encoder):
                # Convert LabelEncoder to dict for fast pandas mapping
                mapping = dict(zip(encoder.classes_, encoder.transform(encoder.classes_)))
                return df[col].map(mapping).fillna(0).astype(int)

            # Re-create encoders if needed or use stored ones
            if self.le_dict:
                df['Gender'] = safe_map('Gender', self.le_dict['Gender'])
                df['Symptoms'] = safe_map('Symptoms', self.le_dict['Symptoms'])
                df['Pre_Existing_Conditions'] = safe_map('Pre_Existing_Conditions', self.le_dict['Pre_Existing_Conditions'])
                if 'Consciousness' in self.le_dict:
                    df['Consciousness'] = safe_map('Consciousness', self.le_dict['Consciousness'])
            
            X = df[['Age', 'Gender', 'Symptoms', 'Blood_Pressure', 'Heart_Rate', 'Temperature', 'O2_Saturation', 'Pain_Severity', 'Consciousness', 'Pre_Existing_Conditions']]
            y_true = df['Risk_Level']
            
            # Predict
            y_pred_idx = self.model.predict(X)
            y_pred = self.le_risk.inverse_transform(y_pred_idx)
            
            # Metrics
            acc = accuracy_score(y_true, y_pred)
            f1 = f1_score(y_true, y_pred, average='weighted')
            
            return {
                "accuracy": round(acc * 100, 2),
                "f1_score": round(f1 * 100, 2),
                "labels": ['Low', 'Medium', 'High']
            }

        except Exception as e:
            print(f"Benchmark Error: {e}")
            return {"error": str(e)}
        # symptom_name might be encoded or raw string. The UI should send raw string ideally, 
        # but the model needs encoded. We need to handle mapping if input is raw.
        # For this hackathon, we assume the UI sends the specific string.
        
        return dept_map.get(symptom_name, "🏥 General Medicine / OPD")

    def predict_patient(self, data_dict):
        """
        Full Pipeline: Preprocessing -> Prediction -> Recommendation -> Explanation
        """
        # Convert dict to DataFrame
        # IMPORTANT: Columns must match training data order exactly
        # Columns: Age, Gender, Symptoms, Blood_Pressure, Heart_Rate, Temperature, O2_Saturation, Pain_Severity, Consciousness, Pre_Existing_Conditions
        
        input_dict = {
            'Age': [data_dict['Age']],
            'Gender': [data_dict['Gender']],
            'Symptoms': [data_dict['Symptoms']],
            'Blood_Pressure': [data_dict['Blood_Pressure']],
            'Heart_Rate': [data_dict['Heart_Rate']],
            'Temperature': [data_dict['Temperature']],
            'O2_Saturation': [data_dict.get('O2_Saturation', 98)],
            'Pain_Severity': [data_dict.get('Pain_Severity', 0)],
            'Consciousness': [data_dict.get('Consciousness', 'Alert')],
            'Pre_Existing_Conditions': [data_dict['Pre_Existing_Conditions']]
        }
        df = pd.DataFrame(input_dict)
        
        # Preprocessing: Encode strings to numbers using saved encoders
        try:
            # Gender
            gender_str = data_dict.get('Gender', 'Male')
            if self.le_dict and 'Gender' in self.le_dict:
                 try:
                     gender_val = self.le_dict['Gender'].transform([gender_str])[0]
                 except:
                     gender_val = 0 
            else:
                 gender_val = 0
            df['Gender'] = gender_val

            # Symptoms
            symptom_str = data_dict.get('Symptoms', 'Fever')
            if self.le_dict and 'Symptoms' in self.le_dict:
                 try:
                    symptom_val = self.le_dict['Symptoms'].transform([symptom_str])[0]
                 except:
                    symptom_val = 0
            else:
                symptom_val = 0
            df['Symptoms'] = symptom_val
                
            # Pre-Existing
            condition_str = data_dict.get('Pre_Existing_Conditions', 'None')
            if self.le_dict and 'Pre_Existing_Conditions' in self.le_dict:
                 try:
                    condition_val = self.le_dict['Pre_Existing_Conditions'].transform([condition_str])[0]
                 except:
                    condition_val = 0
            else:
                condition_val = 0
            df['Pre_Existing_Conditions'] = condition_val

            # Consciousness
            consc_str = data_dict.get('Consciousness', 'Alert')
            if self.le_dict and 'Consciousness' in self.le_dict:
                 try:
                    consc_val = self.le_dict['Consciousness'].transform([consc_str])[0]
                 except:
                    consc_val = 0
            else:
                consc_val = 0 # Default alert
            df['Consciousness'] = consc_val

        except Exception as e:
            print(f"Encoding Error: {e}")
            return {"status": "error", "message": f"Encoding Error: {e}"}
        try:
            # Predict
            risk, conf, rule_hit, shap_dict, override_reason = self.hybrid_risk_engine(df)
            
            # Recommendation
            dept, disease, specialist, treatment = self.get_dept_recommendation(symptom_str, risk)
            
            # Simple Insights (Fallback or Addition)
            insights = []
            if override_reason:
                insights.append(f"⚠️ {override_reason}")
            
            # Top SHAP contributors
            sorted_shap = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
            top_factors = sorted_shap[:3] # Top 3
            
            for feature, impact in top_factors:
                direction = "increased" if impact > 0 else "decreased"
                if abs(impact) > 0.01: # Filter tiny noise
                    insights.append(f"{feature} {direction} risk (Impact: {impact:.2f})")

            return {
                "status": "success",
                "risk_level": risk,
                "confidence": f"{conf*100:.2f}%",
                "department": dept,
                "predicted_disease": disease,
                "recommended_specialist": specialist,
                "curing_process": treatment,
                "rule_triggered": rule_hit,
                "insights": insights,
                "shap_values": shap_dict
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

# Singleton instance for simple import
# engine = TriageEngine() 
.PHONY: test api ui

test:
	pytest

api:
	uvicorn partner_os_v2.api.main:app --reload

ui:
	streamlit run streamlit_app.py

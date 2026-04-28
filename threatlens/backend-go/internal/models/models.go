package models

type IOCAnalysis struct {
	ID              int                    `json:"id"`
	CaseID          string                 `json:"case_id"`
	IOC             string                 `json:"ioc"`
	IOCType         string                 `json:"ioc_type"`
	Score           int                    `json:"score"`
	RiskLevel       string                 `json:"risk_level"`
	ConfidenceLevel string                 `json:"confidence_level"`
	Recommendation  string                 `json:"recommendation"`
	Summary         string                 `json:"summary"`
	Sources         map[string]string      `json:"sources"`
	Evidence        map[string]any         `json:"evidence"`
	ScoreBreakdown  []string               `json:"score_breakdown"`
	KQL             string                 `json:"kql"`
	AnalystDecision string                 `json:"analyst_decision"`
	AnalystNotes    string                 `json:"analyst_notes"`
	CaseStatus      string                 `json:"case_status"`
	AIAnalysis      map[string]any         `json:"ai_analysis"`
	CreatedAt       string                 `json:"created_at"`
	UpdatedAt       string                 `json:"updated_at"`
}

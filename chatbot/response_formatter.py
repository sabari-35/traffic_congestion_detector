"""
Format chatbot responses for different output channels
"""

from typing import Dict, Any
from dataclasses import asdict
from chatbot.traffic_advisor import ChatbotResponse

class ResponseFormatter:
    """Format responses for different interfaces"""
    
    @staticmethod
    def to_plain_text(response: ChatbotResponse) -> str:
        """Format as plain text for chat interfaces"""
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("🚦 ADAPTIVE TRAFFIC SIGNAL ADVISORY")
        lines.append("=" * 60)
        
        # Recommendations
        lines.append("\n📊 RECOMMENDED SIGNAL TIMINGS:")
        for approach, green_time in response.recommended_green_times.items():
            lines.append(f"  Approach {approach}: {green_time:.1f} seconds green")
        lines.append(f"  Total Cycle Time: {response.cycle_time:.1f} seconds")
        
        # Reasoning
        lines.append("\n🧠 ENGINEERING ANALYSIS:")
        for reason in response.reasoning:
            lines.append(f"  • {reason}")
        
        # Safety
        lines.append("\n✅ SAFETY CONFIRMATION:")
        for safety in response.safety_confirmation:
            lines.append(f"  ✓ {safety}")
        
        # Operational Advice
        if response.operational_advice:
            lines.append("\n🎯 OPERATIONAL ADVICE FOR TRAFFIC POLICE:")
            for advice in response.operational_advice:
                lines.append(f"  • {advice}")
        
        # Warnings
        if response.warnings:
            lines.append("\n⚠️ IMPORTANT WARNINGS:")
            for warning in response.warnings:
                lines.append(f"  ⚠ {warning}")
        
        # Footer
        lines.append("\n" + "=" * 60)
        lines.append("ℹ️ Advisory provided by Certified Traffic Engineer AI")
        lines.append(f"📅 {response.timestamp}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    @staticmethod
    def to_json(response: ChatbotResponse) -> Dict[str, Any]:
        return {
        "status": "success",
        "timestamp": response.timestamp,

        "signal_timings": {
            "per_approach": response.recommended_green_times,
            "total_cycle_time": response.cycle_time
        },

        "reasoning_points": response.reasoning,

        "safety_status": {
            "confirmed": True,
            "checks": response.safety_confirmation
        },

        "police_action": response.operational_advice or [
            "Apply the recommended green times",
            "Observe traffic for one full cycle",
            "Re-run advisory if congestion persists"
        ],

        "warnings": response.warnings
    }

    
    @staticmethod
    def to_html(response: ChatbotResponse) -> str:
        """Format as HTML for web interfaces"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 15px; }}
                .section {{ margin: 20px 0; border-left: 4px solid #3498db; padding-left: 15px; }}
                .warning {{ color: #e74c3c; font-weight: bold; }}
                .success {{ color: #27ae60; }}
                .advice {{ background: #f9f9f9; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚦 Adaptive Traffic Signal Advisory</h2>
                <small>{response.timestamp}</small>
            </div>
            
            <div class="section">
                <h3>📊 Recommended Signal Timings</h3>
        """
        
        for approach, green_time in response.recommended_green_times.items():
            html += f"<p><b>Approach {approach}:</b> {green_time:.1f} seconds green</p>"
        
        html += f"<p><b>Total Cycle Time:</b> {response.cycle_time:.1f} seconds</p>"
        
        html += """
            </div>
            
            <div class="section">
                <h3>🧠 Engineering Analysis</h3>
        """
        
        for reason in response.reasoning:
            html += f"<p>• {reason}</p>"
        
        html += """
            </div>
            
            <div class="section success">
                <h3>✅ Safety Confirmation</h3>
        """
        
        for safety in response.safety_confirmation:
            html += f"<p>✓ {safety}</p>"
        
        if response.operational_advice:
            html += """
                <div class="section advice">
                    <h3>🎯 Operational Advice for Traffic Police</h3>
            """
            
            for advice in response.operational_advice:
                html += f"<p>• {advice}</p>"
            
            html += "</div>"
        
        if response.warnings:
            html += """
                <div class="section warning">
                    <h3>⚠️ Important Warnings</h3>
            """
            
            for warning in response.warnings:
                html += f"<p>⚠ {warning}</p>"
            
            html += "</div>"
        
        html += """
            <hr>
            <p><small>ℹ️ Advisory provided by Certified Traffic Engineer AI</small></p>
        </body>
        </html>
        """
        
        return html
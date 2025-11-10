import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { AlertCircle, RefreshCw, Download } from "lucide-react"

export default function SettingsView() {
  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-foreground mb-2">Settings</h1>
        <p className="text-muted-foreground">Configure model and system parameters</p>
      </div>

      {/* Model Configuration */}
      <Card className="bg-card border-border p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4">Model Configuration</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Retraining Interval</label>
            <select className="w-full bg-input border border-border rounded-lg px-3 py-2 text-foreground">
              <option>Every 2 hours</option>
              <option>Every 4 hours</option>
              <option>Every 6 hours</option>
              <option>Every 12 hours</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Learning Algorithm</label>
            <select className="w-full bg-input border border-border rounded-lg px-3 py-2 text-foreground">
              <option>LSTM + Ensemble</option>
              <option>Transformer</option>
              <option>Random Forest</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Look-back Period</label>
            <select className="w-full bg-input border border-border rounded-lg px-3 py-2 text-foreground">
              <option>30 days</option>
              <option>60 days</option>
              <option>90 days</option>
              <option>1 year</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Data Management */}
      <Card className="bg-card border-border p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4">Data Management</h2>
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-input rounded-lg border border-border">
            <div>
              <p className="font-semibold text-foreground">Export Training Data</p>
              <p className="text-sm text-muted-foreground">Download model training datasets</p>
            </div>
            <Button variant="outline" className="border-border gap-2 bg-transparent">
              <Download className="w-4 h-4" />
              Export
            </Button>
          </div>

          <div className="flex justify-between items-center p-3 bg-input rounded-lg border border-border">
            <div>
              <p className="font-semibold text-foreground">Clear Cache</p>
              <p className="text-sm text-muted-foreground">Remove cached predictions</p>
            </div>
            <Button variant="outline" className="border-border gap-2 bg-transparent">
              <RefreshCw className="w-4 h-4" />
              Clear
            </Button>
          </div>
        </div>
      </Card>

      {/* Advanced Settings */}
      <Card className="bg-card border-border p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-accent" />
          Advanced Settings
        </h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold text-foreground">Auto-rebalance Portfolio</p>
              <p className="text-sm text-muted-foreground">Automatically rebalance based on predictions</p>
            </div>
            <input type="checkbox" className="w-5 h-5" defaultChecked />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold text-foreground">Enable Email Alerts</p>
              <p className="text-sm text-muted-foreground">Get notified of significant changes</p>
            </div>
            <input type="checkbox" className="w-5 h-5" defaultChecked />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold text-foreground">Ensemble Learning</p>
              <p className="text-sm text-muted-foreground">Use multiple models for predictions</p>
            </div>
            <input type="checkbox" className="w-5 h-5" defaultChecked />
          </div>
        </div>
      </Card>

      {/* Save Settings */}
      <div className="flex gap-2">
        <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">Save Changes</Button>
        <Button variant="outline" className="border-border bg-transparent">
          Cancel
        </Button>
      </div>
    </div>
  )
}

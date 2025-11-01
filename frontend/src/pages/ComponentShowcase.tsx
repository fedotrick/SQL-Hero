import { useState } from "react";
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Badge,
  ProgressBar,
  CircularProgress,
} from "../components/ui";
import { Plus, Download, Heart, Star } from "lucide-react";

export const ComponentShowcase = () => {
  const [progress, setProgress] = useState(65);

  return (
    <div className="min-h-screen bg-telegram-bg pb-20">
      <div className="max-w-telegram mx-auto p-4 space-y-8">
        <header className="text-center py-6">
          <h1 className="text-3xl font-bold text-telegram-text mb-2">UI Components Showcase</h1>
          <p className="text-telegram-subtitle">Reusable UI primitives for the application</p>
        </header>

        <section>
          <h2 className="text-2xl font-semibold text-telegram-text mb-4">Buttons</h2>
          <Card>
            <CardHeader>
              <CardTitle>Button Variants</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <Button variant="primary">Primary</Button>
                  <Button variant="secondary">Secondary</Button>
                  <Button variant="outline">Outline</Button>
                  <Button variant="ghost">Ghost</Button>
                  <Button variant="destructive">Destructive</Button>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">Sizes</h4>
                  <div className="flex flex-wrap items-center gap-2">
                    <Button size="sm">Small</Button>
                    <Button size="md">Medium</Button>
                    <Button size="lg">Large</Button>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">With Icons</h4>
                  <div className="flex flex-wrap gap-2">
                    <Button leftIcon={<Plus size={16} />}>Add Item</Button>
                    <Button rightIcon={<Download size={16} />} variant="secondary">
                      Download
                    </Button>
                    <Button leftIcon={<Heart size={16} />} variant="outline">
                      Like
                    </Button>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">States</h4>
                  <div className="flex flex-wrap gap-2">
                    <Button disabled>Disabled</Button>
                    <Button isLoading>Loading</Button>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">Full Width</h4>
                  <Button fullWidth>Full Width Button</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-telegram-text mb-4">Cards</h2>
          <div className="space-y-4">
            <Card variant="default">
              <CardHeader>
                <CardTitle>Default Card</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-telegram-subtitle">
                  This is a default card with standard background styling.
                </p>
              </CardContent>
            </Card>

            <Card variant="elevated">
              <CardHeader>
                <CardTitle>Elevated Card</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-telegram-subtitle">
                  This card has a shadow for elevation effect.
                </p>
              </CardContent>
            </Card>

            <Card variant="outlined">
              <CardHeader>
                <CardTitle>Outlined Card</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-telegram-subtitle">This card has a border outline.</p>
              </CardContent>
            </Card>

            <Card interactive padding="md">
              <CardHeader>
                <CardTitle>Interactive Card</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-telegram-subtitle">
                  Click or hover on this card to see the interaction effects.
                </p>
              </CardContent>
            </Card>

            <div className="grid grid-cols-2 gap-4">
              <Card padding="sm">
                <CardContent>Small Padding</CardContent>
              </Card>
              <Card padding="lg">
                <CardContent>Large Padding</CardContent>
              </Card>
            </div>
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-telegram-text mb-4">Badges</h2>
          <Card>
            <CardHeader>
              <CardTitle>Badge Variants</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  <Badge variant="default">Default</Badge>
                  <Badge variant="success">Success</Badge>
                  <Badge variant="warning">Warning</Badge>
                  <Badge variant="error">Error</Badge>
                  <Badge variant="info">Info</Badge>
                  <Badge variant="outline">Outline</Badge>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">Sizes</h4>
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge size="sm">Small</Badge>
                    <Badge size="md">Medium</Badge>
                    <Badge size="lg">Large</Badge>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">
                    With Dot Indicator
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="success" dot>
                      Active
                    </Badge>
                    <Badge variant="error" dot>
                      Inactive
                    </Badge>
                    <Badge variant="warning" dot>
                      Pending
                    </Badge>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">Usage Example</h4>
                  <div className="flex items-center gap-2">
                    <span className="text-telegram-text">Level 5</span>
                    <Badge variant="info" size="sm">
                      <Star size={12} />
                      Pro
                    </Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-telegram-text mb-4">Progress Bars</h2>
          <Card>
            <CardHeader>
              <CardTitle>Progress Indicators</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">
                    Linear Progress
                  </h4>
                  <div className="space-y-3">
                    <ProgressBar value={progress} showLabel label="Course Progress" />
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => setProgress(Math.max(0, progress - 10))}
                      >
                        -10%
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => setProgress(Math.min(100, progress + 10))}
                      >
                        +10%
                      </Button>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">Sizes</h4>
                  <div className="space-y-2">
                    <ProgressBar value={75} size="sm" />
                    <ProgressBar value={75} size="md" />
                    <ProgressBar value={75} size="lg" />
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">Variants</h4>
                  <div className="space-y-2">
                    <ProgressBar value={65} variant="default" showLabel label="Default" />
                    <ProgressBar value={100} variant="success" showLabel label="Success" />
                    <ProgressBar value={40} variant="warning" showLabel label="Warning" />
                    <ProgressBar value={20} variant="error" showLabel label="Error" />
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">
                    Circular Progress
                  </h4>
                  <div className="flex flex-wrap gap-4">
                    <CircularProgress value={progress} />
                    <CircularProgress value={progress} variant="success" />
                    <CircularProgress value={progress} variant="warning" />
                    <CircularProgress value={progress} variant="error" />
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-telegram-subtitle mb-2">
                    Circular Sizes
                  </h4>
                  <div className="flex flex-wrap items-center gap-4">
                    <CircularProgress value={75} size={48} strokeWidth={3} />
                    <CircularProgress value={75} size={64} strokeWidth={4} />
                    <CircularProgress value={75} size={80} strokeWidth={5} />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-telegram-text mb-4">Component Combinations</h2>
          <div className="space-y-4">
            <Card interactive>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Achievement Unlocked!</CardTitle>
                  <Badge variant="success" dot>
                    New
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <p className="text-telegram-subtitle">
                    You've completed 10 lessons. Keep up the great work!
                  </p>
                  <ProgressBar value={100} variant="success" size="sm" />
                  <div className="flex gap-2">
                    <Button size="sm" fullWidth>
                      View Details
                    </Button>
                    <Button size="sm" variant="outline" fullWidth>
                      Share
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Weekly Progress</CardTitle>
                  <Badge variant="info" size="sm">
                    Level 5
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <CircularProgress value={85} size={80} />
                    <div className="flex-1 ml-4 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-telegram-text">Lessons Completed</span>
                        <span className="text-telegram-subtitle">17/20</span>
                      </div>
                      <ProgressBar value={85} size="sm" animated={false} />
                    </div>
                  </div>
                  <Button fullWidth leftIcon={<Star size={16} />}>
                    Continue Learning
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        <section className="pb-4">
          <Card>
            <CardHeader>
              <CardTitle>Design System Info</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm text-telegram-subtitle">
                <p>✓ All components use Telegram design tokens</p>
                <p>✓ Responsive and mobile-optimized</p>
                <p>✓ Smooth animations with Framer Motion</p>
                <p>✓ Dark mode support through CSS variables</p>
                <p>✓ Accessible and semantic HTML</p>
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </div>
  );
};

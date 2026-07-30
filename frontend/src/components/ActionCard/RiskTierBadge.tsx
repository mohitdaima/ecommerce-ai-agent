import { Badge } from '@/components/ui/Badge';
import { RISK_TIERS } from '@/config/app.config';
import type { RiskTier } from '@/types';

export function RiskTierBadge({ tier }: { tier: RiskTier }) {
  const meta = RISK_TIERS[tier];
  return (
    <Badge fgVar={meta.fgVar} bgVar={meta.bgVar} title={meta.description}>
      {meta.label}
    </Badge>
  );
}

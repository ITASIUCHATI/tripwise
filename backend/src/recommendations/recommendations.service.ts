import {
    BadGatewayException,
    Injectable,
} from '@nestjs/common';

import { TripsService } from '../trips/trips.service';

@Injectable()
export class RecommendationsService {
    constructor(
        private readonly tripsService: TripsService,
    ) {}

    async plan(
        input: any,
        userId: number,
    ) {
        const mlServiceUrl =
            process.env.ML_SERVICE_URL ||
            'http://localhost:8000';

        try {
            const response = await fetch(
                `${mlServiceUrl}/plan`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type':
                            'application/json',
                    },
                    body: JSON.stringify(input),
                },
            );

            if (!response.ok) {
                throw new Error(
                    await response.text(),
                );
            }

            const result = await response.json();

            await this.tripsService.create({
                ...input,
                result,
                userId,
            });

            return result;
        } catch {
            throw new BadGatewayException(
                'ML service is unavailable',
            );
        }
    }
}

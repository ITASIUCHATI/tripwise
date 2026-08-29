import {
    BadGatewayException,
    BadRequestException,
    Injectable,
} from '@nestjs/common';

import { TripsService } from '../trips/trips.service';

@Injectable()
export class RecommendationsService {
    constructor(
        private readonly tripsService: TripsService,
    ) {}

    async suggestDestination(
        destination: string,
    ) {
        const mlServiceUrl =
            process.env.ML_SERVICE_URL ||
            'http://localhost:8000';

        try {
            const response = await fetch(
                `${mlServiceUrl}/suggest-destination`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        destination,
                    }),
                },
            );

            const body = await response.json();

            if (!response.ok) {
                throw new Error(
                    JSON.stringify(body),
                );
            }

            return body;
        } catch (error) {
            throw new BadGatewayException(
                'ML service is unavailable',
            );
        }
    }

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
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        destination:
                            input.destination,
                        days: Number(input.days),
                        people: Number(input.people),
                        interests:
                            input.interests ||
                            'nature,food',
                    }),
                },
            );

            const body = await response.json();

            if (response.status === 400) {
                throw new BadRequestException(
                    body?.detail ||
                        'Invalid trip details',
                );
            }

            if (!response.ok) {
                throw new Error(
                    JSON.stringify(body),
                );
            }

            await this.tripsService.create({
                destination: body.destination,
                days: body.days,
                budget: body.predicted_cost,
                people: body.people,
                interests: body.interests,
                style: 'balanced',
                result: body,
                userId,
            });

            return body;
        } catch (error) {
            if (
                error instanceof BadRequestException
            ) {
                throw error;
            }

            throw new BadGatewayException(
                'ML service is unavailable',
            );
        }
    }
}
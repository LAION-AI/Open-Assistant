import React from "react";
import { Box, Button, Center, Link, Text } from "@chakra-ui/react";
import { FiAlertTriangle } from "react-icons/fi";
import { EmptyState } from "src/components/EmptyState";
import { getDashboardLayout } from "src/components/Layout";

export default function Guide() {
  return (
    <>
      <Center flexDirection="column" gap="4" fontSize="lg" className="subpixel-antialiased">
        <EmptyState
          text="Sorry, we encountered a server error. We're not sure what went wrong."
          icon={FiAlertTriangle}
        />
        <Box display="flex" flexDirection="column" alignItems="center" gap="2" mt="6">
          <Text fontSize="sm">If you were trying to contribute data but ended up here, please file a bug.</Text>
          <Button
            width="fit-content"
            leftIcon={<FiAlertTriangle className="text-blue-500" aria-hidden="true" />}
            variant="solid"
            size="xs"
          >
            <Link
              key="Report a Bug"
              href="https://github:com/LAION-AI/Open-Assistant/issues/new/choose"
              aria-label="Report a Bug"
              className="flex items-center"
              _hover={{ textDecoration: "none" }}
              isExternal
            >
              Report a Bug
            </Link>
          </Button>
        </Box>
      </Center>
    </>
  );
}

Guide.getLayout = getDashboardLayout;
